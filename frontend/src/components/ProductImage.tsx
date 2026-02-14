import { useState, useEffect, useRef } from 'react';

// In-memory cache shared across all instances
const imageCache = new Map<string, string | null>();
const STORAGE_KEY = 'product-img-cache-v1';

// Load cache from localStorage on module init
try {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    const entries: Record<string, string> = JSON.parse(saved);
    for (const [k, v] of Object.entries(entries)) {
      imageCache.set(k, v);
    }
  }
} catch { /* ignore */ }

function saveCache() {
  try {
    const obj: Record<string, string> = {};
    imageCache.forEach((v, k) => { if (v) obj[k] = v; });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(obj));
  } catch { /* ignore */ }
}

// Extract English brand/model keywords from a product name
function extractSearchQuery(name: string): string {
  // Get English words (brand names, model numbers)
  const english = name.match(/[A-Za-z][A-Za-z0-9.'+\-]*/g) || [];
  if (english.length > 0) {
    // Take up to 4 English words for the search
    return english.slice(0, 4).join(' ');
  }
  return '';
}

// Fetch product image from Wikipedia
async function fetchImage(productName: string): Promise<string | null> {
  const query = extractSearchQuery(productName);
  if (!query) return null;

  try {
    // Search Wikipedia for the product
    const searchUrl = `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(query)}&format=json&origin=*&srlimit=1`;
    const searchRes = await fetch(searchUrl);
    if (!searchRes.ok) return null;
    const searchData = await searchRes.json();

    const results = searchData?.query?.search;
    if (!results?.length) return null;

    // Get the page summary which includes a thumbnail
    const title = encodeURIComponent(results[0].title);
    const summaryUrl = `https://en.wikipedia.org/api/rest_v1/page/summary/${title}`;
    const summaryRes = await fetch(summaryUrl);
    if (!summaryRes.ok) return null;
    const summaryData = await summaryRes.json();

    return summaryData?.thumbnail?.source || null;
  } catch {
    return null;
  }
}

// Queue to limit concurrent requests
const queue: (() => void)[] = [];
let running = 0;
const MAX_CONCURRENT = 3;

function enqueue(fn: () => Promise<void>) {
  const run = async () => {
    running++;
    await fn();
    running--;
    if (queue.length > 0) {
      const next = queue.shift()!;
      next();
    }
  };
  if (running < MAX_CONCURRENT) {
    run();
  } else {
    queue.push(run);
  }
}

interface ProductImageProps {
  productName: string;
  fallbackUrl: string;
  alt: string;
  className?: string;
}

export default function ProductImage({ productName, fallbackUrl, alt, className }: ProductImageProps) {
  const [src, setSrc] = useState<string>(fallbackUrl);
  const [loaded, setLoaded] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const fetchedRef = useRef(false);

  useEffect(() => {
    // Check cache first
    if (imageCache.has(productName)) {
      const cached = imageCache.get(productName);
      if (cached) setSrc(cached);
      return;
    }

    // Use IntersectionObserver for lazy loading
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !fetchedRef.current) {
          fetchedRef.current = true;
          observer.disconnect();

          enqueue(async () => {
            const url = await fetchImage(productName);
            imageCache.set(productName, url);
            saveCache();
            if (url) setSrc(url);
          });
        }
      },
      { rootMargin: '200px' }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, [productName]);

  return (
    <div ref={containerRef} className="relative w-full h-full">
      <img
        src={src}
        alt={alt}
        className={`${className || ''} ${loaded ? 'opacity-100' : 'opacity-0'} transition-opacity duration-300`}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        onError={() => {
          if (src !== fallbackUrl) {
            setSrc(fallbackUrl);
          }
        }}
      />
      {!loaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 animate-pulse">
          <svg className="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      )}
    </div>
  );
}
