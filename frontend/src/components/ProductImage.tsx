import { useState, useEffect, useRef } from 'react';

// In-memory cache shared across all instances
const imageCache = new Map<string, string | null>();
const STORAGE_KEY = 'product-img-cache-v2';

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
  const english = name.match(/[A-Za-z][A-Za-z0-9.'+\-]*/g) || [];
  if (english.length > 0) {
    return english.slice(0, 4).join(' ');
  }
  return '';
}

// Fetch product image from Wikipedia
async function fetchImage(productName: string): Promise<string | null> {
  const query = extractSearchQuery(productName);
  if (!query) return null;

  try {
    const searchUrl = `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(query)}&format=json&origin=*&srlimit=1`;
    const searchRes = await fetch(searchUrl);
    if (!searchRes.ok) return null;
    const searchData = await searchRes.json();

    const results = searchData?.query?.search;
    if (!results?.length) return null;

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

// Generate a consistent color from a string
function nameToColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const h = Math.abs(hash) % 360;
  return `hsl(${h}, 35%, 25%)`;
}

interface ProductImageProps {
  productName: string;
  fallbackUrl: string;
  alt: string;
  className?: string;
}

export default function ProductImage({ productName, alt }: ProductImageProps) {
  const [imgUrl, setImgUrl] = useState<string | null>(() => {
    const cached = imageCache.get(productName);
    return cached || null;
  });
  const [imgLoaded, setImgLoaded] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const fetchedRef = useRef(false);

  useEffect(() => {
    if (imageCache.has(productName)) {
      const cached = imageCache.get(productName);
      if (cached) setImgUrl(cached);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !fetchedRef.current) {
          fetchedRef.current = true;
          observer.disconnect();

          enqueue(async () => {
            const url = await fetchImage(productName);
            imageCache.set(productName, url);
            saveCache();
            if (url) setImgUrl(url);
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

  const bgColor = nameToColor(productName);

  // Extract brand name for display
  const brandMatch = productName.match(/[A-Za-z][A-Za-z0-9.'+\-]*/);
  const brand = brandMatch ? brandMatch[0] : '';

  return (
    <div ref={containerRef} className="relative w-full h-full overflow-hidden">
      {/* Always-visible text fallback */}
      <div
        className="absolute inset-0 flex flex-col items-center justify-center p-3 text-center"
        style={{ backgroundColor: bgColor }}
      >
        {brand && (
          <span className="text-white/90 text-lg font-bold mb-1 drop-shadow">{brand}</span>
        )}
        <span className="text-white/70 text-xs leading-tight line-clamp-2 max-w-[90%]">
          {productName}
        </span>
      </div>

      {/* Real image from Wikipedia (fades in on top when loaded) */}
      {imgUrl && (
        <img
          src={imgUrl}
          alt={alt}
          className={`absolute inset-0 w-full h-full object-contain bg-white transition-opacity duration-300 ${imgLoaded ? 'opacity-100' : 'opacity-0'}`}
          loading="lazy"
          onLoad={() => setImgLoaded(true)}
          onError={() => {
            setImgUrl(null);
            setImgLoaded(false);
          }}
        />
      )}
    </div>
  );
}
