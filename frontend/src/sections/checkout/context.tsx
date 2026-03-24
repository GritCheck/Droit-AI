import { createContext, useContext } from 'react';

interface CheckoutContextType {
  // Add checkout context properties as needed
}

const CheckoutContext = createContext<CheckoutContextType | undefined>(undefined);

export function useCheckoutContext() {
  const context = useContext(CheckoutContext);
  if (context === undefined) {
    throw new Error('useCheckoutContext must be used within a CheckoutProvider');
  }
  return context;
}

export { CheckoutContext };
