import { ProductWithPrices, PriceInfo } from '../types/product';

interface PriceComparisonTableProps {
  product: ProductWithPrices;
}

const isValidUrl = (url: string): boolean => {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
};

export default function PriceComparisonTable({ product }: PriceComparisonTableProps) {
  const formatPrice = (price: number) => {
    return `₪${price.toLocaleString('he-IL')}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('he-IL', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getBestPrice = (): PriceInfo | undefined => {
    const availablePrices = product.prices.filter(p => p.availability);
    if (availablePrices.length === 0) return undefined;
    return availablePrices.reduce((min, price) =>
      price.price < min.price ? price : min
    );
  };

  const bestPrice = getBestPrice();

  return (
    <div className="card p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{product.name}</h2>
        {product.description && (
          <p className="text-gray-600">{product.description}</p>
        )}
      </div>

      {/* Price Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <div className="text-sm text-green-700 mb-1">המחיר הנמוך</div>
          <div className="text-2xl font-bold text-green-600">
            {product.lowest_price ? formatPrice(product.lowest_price) : 'N/A'}
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="text-sm text-blue-700 mb-1">מחיר ממוצע</div>
          <div className="text-2xl font-bold text-blue-600">
            {product.average_price ? formatPrice(product.average_price) : 'N/A'}
          </div>
        </div>

        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
          <div className="text-sm text-red-700 mb-1">המחיר הגבוה</div>
          <div className="text-2xl font-bold text-red-600">
            {product.highest_price ? formatPrice(product.highest_price) : 'N/A'}
          </div>
        </div>
      </div>

      {/* Price Comparison Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-200">
              <th className="text-right py-3 px-4 text-gray-700 font-semibold">חנות</th>
              <th className="text-right py-3 px-4 text-gray-700 font-semibold">מחיר</th>
              <th className="text-right py-3 px-4 text-gray-700 font-semibold">זמינות</th>
              <th className="text-right py-3 px-4 text-gray-700 font-semibold">עדכון אחרון</th>
              <th className="text-left py-3 px-4 text-gray-700 font-semibold">פעולה</th>
            </tr>
          </thead>
          <tbody>
            {product.prices.map((priceInfo) => {
              const isBestPrice = bestPrice?.source === priceInfo.source;

              return (
                <tr
                  key={priceInfo.source}
                  className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                    isBestPrice ? 'bg-green-50' : ''
                  }`}
                >
                  {/* Store */}
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">{priceInfo.source}</span>
                      {isBestPrice && (
                        <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full font-bold">
                          המחיר הטוב
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Price */}
                  <td className="py-4 px-4">
                    <span className={`text-lg font-bold ${
                      isBestPrice ? 'text-green-600' : 'text-gray-900'
                    }`}>
                      {formatPrice(priceInfo.price)}
                    </span>
                    <span className="text-sm text-gray-500 ml-1">{priceInfo.currency}</span>
                  </td>

                  {/* Availability */}
                  <td className="py-4 px-4">
                    {priceInfo.availability ? (
                      <span className="inline-flex items-center gap-1 text-green-600">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        במלאי
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-red-600">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        אזל מהמלאי
                      </span>
                    )}
                  </td>

                  {/* Last Updated */}
                  <td className="py-4 px-4 text-sm text-gray-500">
                    {formatDate(priceInfo.last_updated)}
                  </td>

                  {/* Action */}
                  <td className="py-4 px-4 text-right">
                    {priceInfo.availability && priceInfo.url && isValidUrl(priceInfo.url) && (
                      <a
                        href={priceInfo.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-primary-600 hover:text-primary-700 font-medium"
                      >
                        לחנות
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Out of stock warning */}
      {!bestPrice && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-red-800 font-medium">כל המוצרים אזלו מהמלאי כרגע</span>
          </div>
        </div>
      )}

      {/* Savings Info */}
      {product.lowest_price && product.highest_price && (
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
            </svg>
            <span className="text-yellow-800 font-medium">
              אפשר לחסוך עד {formatPrice(product.highest_price - product.lowest_price)} בבחירת המחיר הנמוך ביותר!
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
