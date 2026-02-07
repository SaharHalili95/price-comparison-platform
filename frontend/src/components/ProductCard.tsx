import { ProductWithPrices } from '../types/product';

interface ProductCardProps {
  product: ProductWithPrices;
  onViewDetails?: (productId: number) => void;
}

export default function ProductCard({ product, onViewDetails }: ProductCardProps) {
  const formatPrice = (price: number | undefined) => {
    if (!price) return 'N/A';
    return `₪${price.toLocaleString('he-IL')}`;
  };

  const getSavingsPercentage = () => {
    if (!product.lowest_price || !product.highest_price) return 0;
    const savings = ((product.highest_price - product.lowest_price) / product.highest_price) * 100;
    return Math.round(savings);
  };

  const savings = getSavingsPercentage();

  return (
    <div className="card p-0 flex flex-col h-full">
      {/* Product Image */}
      <div className="relative h-48 bg-gray-200 overflow-hidden">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover"
            loading="lazy"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-300">
            <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}

        {/* Savings Badge */}
        {savings > 0 && (
          <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-bold">
            חסכו {savings}%
          </div>
        )}

        {/* Category Badge */}
        {product.category && (
          <div className="absolute top-2 left-2 bg-primary-600 text-white px-2 py-1 rounded text-xs">
            {product.category}
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="p-4 flex-1 flex flex-col">
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {product.name}
        </h3>

        {product.description && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
            {product.description}
          </p>
        )}

        {/* Price Range */}
        <div className="mt-auto">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">טווח מחירים:</span>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-green-600">
                {formatPrice(product.lowest_price)}
              </span>
              <span className="text-sm text-gray-400">-</span>
              <span className="text-sm text-gray-500">
                {formatPrice(product.highest_price)}
              </span>
            </div>
          </div>

          {/* Average Price */}
          {product.average_price && (
            <div className="text-xs text-gray-500 mb-3">
              ממוצע: {formatPrice(product.average_price)}
            </div>
          )}

          {/* Available Sources */}
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs text-gray-500">זמין ב:</span>
            <div className="flex gap-1">
              {product.prices.filter(p => p.availability).map((price) => (
                <span
                  key={price.source}
                  className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded"
                >
                  {price.source}
                </span>
              ))}
            </div>
          </div>

          {/* View Details Button */}
          <button
            onClick={() => onViewDetails?.(product.id)}
            className="w-full btn-primary text-sm"
            aria-label={`השוו מחירים עבור ${product.name}`}
          >
            השוו מחירים
          </button>
        </div>
      </div>
    </div>
  );
}
