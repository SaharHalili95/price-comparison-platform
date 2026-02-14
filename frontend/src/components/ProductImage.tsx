interface ProductImageProps {
  productName: string;
  fallbackUrl: string;
  alt: string;
  className?: string;
}

// Generate a consistent color from a string
function nameToColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const h = Math.abs(hash) % 360;
  return `hsl(${h}, 30%, 92%)`;
}

function nameToAccent(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const h = Math.abs(hash) % 360;
  return `hsl(${h}, 40%, 45%)`;
}

export default function ProductImage({ productName }: ProductImageProps) {
  const bgColor = nameToColor(productName);
  const accentColor = nameToAccent(productName);

  // Extract brand name for display
  const brandMatch = productName.match(/[A-Za-z][A-Za-z0-9.'+\-]*/);
  const brand = brandMatch ? brandMatch[0] : '';

  return (
    <div className="relative w-full h-full overflow-hidden" style={{ backgroundColor: bgColor }}>
      <div className="absolute inset-0 flex flex-col items-center justify-center p-4 text-center gap-2">
        {/* Camera icon */}
        <svg
          className="w-10 h-10 opacity-30"
          style={{ color: accentColor }}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>

        {/* Brand name */}
        {brand && (
          <span
            className="text-sm font-bold opacity-60"
            style={{ color: accentColor }}
          >
            {brand}
          </span>
        )}

        {/* Coming soon text */}
        <span
          className="text-xs opacity-40"
          style={{ color: accentColor }}
        >
          תמונה תעלה בקרוב
        </span>
      </div>
    </div>
  );
}
