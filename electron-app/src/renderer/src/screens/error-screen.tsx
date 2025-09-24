import React from 'react';

interface ErrorScreenProps {
    message?: string;
    onRetry?: () => void;
}

export const ErrorScreen: React.FC<ErrorScreenProps> = ({ message = 'Something went wrong.', onRetry }) => {
    return (
        <div className="flex flex-col items-center justify-center h-64 p-6 bg-red-50 border border-red-200 rounded">
            <div className="text-2xl text-red-600 mb-2">Error</div>
            <div className="text-red-500 mb-4">{message}</div>
            {onRetry && (
                <button
                    className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
                    onClick={onRetry}
                >
                    Retry
                </button>
            )}
        </div>
    );
};
