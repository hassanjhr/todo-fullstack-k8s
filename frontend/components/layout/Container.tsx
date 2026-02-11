import { ReactNode } from 'react';

/**
 * Container Component
 * Content wrapper with consistent spacing and max width
 */
interface ContainerProps {
  children: ReactNode;
  className?: string;
}

export default function Container({ children, className = '' }: ContainerProps) {
  return (
    <div className={`mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
}
