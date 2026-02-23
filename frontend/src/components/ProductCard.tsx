import { memo } from 'react';
import { ProductWithPrices } from '../types/product';
import ProductImage from './ProductImage';

interface ProductCardProps {
  product: ProductWithPrices;
  onViewDetails?: (productId: number) => void;
  isFavorite?: boolean;
  onToggleFavorite?: () => void;
}

export default memo(function ProductCard({ product, onViewDetails, isFavorite, onToggleFavorite }: ProductCardProps) {
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
    <article className="card p-0 flex flex-col h-full" aria-label={`מוצר: ${product.name}`}>
      {/* Product Image */}
      <div className="relative h-48 bg-gray-100 overflow-hidden">
        <ProductImage productName={product.name} />

        {/* Favorite Button */}
        {onToggleFavorite && (
          <button
            onClick={(e) => { e.stopPropagation(); onToggleFavorite(); }}
            className="absolute top-2 right-2 z-10 w-9 h-9 flex items-center justify-center rounded-full bg-white/80 backdrop-blur-sm shadow-md hover:bg-white transition-all duration-200 hover:scale-110"
            aria-label={isFavorite ? 'הסר ממועדפים' : 'הוסף למועדפים'}
          >
            <svg className={`w-5 h-5 transition-colors ${isFavorite ? 'text-red-500 fill-red-500' : 'text-gray-400'}`} fill={isFavorite ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
        )}

        {/* Savings Badge */}
        {savings > 0 && (
          <div className={`absolute ${onToggleFavorite ? 'top-12' : 'top-2'} right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-bold`} aria-label={`חסכו ${savings} אחוז`}>
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
    </article>
  );
});
