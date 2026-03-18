/**
 * IngestionStatus Component - Real-time governance tracker
 * Shows document processing pipeline with security metadata
 */

import React, { useState, useEffect } from 'react';
import { CheckCircle, Cloud, Cpu, FileText, Lock, Upload, Search, Shield, Clock } from 'lucide-react';

interface IngestionStatusProps {
  status: 'uploading' | 'parsing' | 'indexing' | 'completed' | 'error';
  file?: string;
  parser?: 'local' | 'azure';
  gids?: string;
  progress?: number;
  error?: string;
  metadata?: {
    chunksCreated?: number;
    chunksIndexed?: number;
    storagePath?: string;
    processingTime?: number;
  };
}

export const IngestionStatus: React.FC<IngestionStatusProps> = ({ 
  status, 
  file = "Unknown Document", 
  parser = 'local', 
  gids = '',
  progress = 0,
  error,
  metadata 
}) => {
  const [currentStep, setCurrentStep] = useState(0);

  // Step progression based on status
  useEffect(() => {
    switch (status) {
      case 'uploading':
        setCurrentStep(0);
        break;
      case 'parsing':
        setCurrentStep(1);
        break;
      case 'indexing':
        setCurrentStep(2);
        break;
      case 'completed':
        setCurrentStep(3);
        break;
      case 'error':
        setCurrentStep(-1);
        break;
    }
  }, [status]);

  const getStepIcon = (step: number) => {
    switch (step) {
      case 0:
        return <Upload size={16} className={currentStep >= 0 ? "text-blue-600" : "text-gray-400"} />;
      case 1:
        return parser === 'local' ? 
          <Cpu size={16} className={currentStep >= 1 ? "text-blue-600" : "text-gray-400"} /> :
          <Cloud size={16} className={currentStep >= 1 ? "text-blue-600" : "text-gray-400"} />;
      case 2:
        return <Search size={16} className={currentStep >= 2 ? "text-blue-600" : "text-gray-400"} />;
      case 3:
        return <CheckCircle size={16} className="text-green-500" />;
      default:
        return <div className="w-4 h-4" />;
    }
  };

  const getStepStatus = (step: number) => {
    if (currentStep === -1) return 'error';
    if (currentStep > step) return 'completed';
    if (currentStep === step) return 'active';
    return 'pending';
  };

  const getStepColor = (stepStatus: string) => {
    switch (stepStatus) {
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'active':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-500 bg-gray-50 border-gray-200';
    }
  };

  const steps = [
    {
      title: 'Upload to Storage',
      description: 'ADLS Gen2 with metadata',
      icon: <Upload size={16} />,
      details: status === 'completed' ? metadata?.storagePath : null
    },
    {
      title: 'Document Parsing',
      description: parser === 'local' ? 'IBM Docling (Local)' : 'Azure Document Intelligence (Cloud)',
      icon: parser === 'local' ? <Cpu size={16} /> : <Cloud size={16} />,
      details: parser === 'local' ? 'Layout-aware Semantic Chunking' : 'High-Fidelity OCR Processing'
    },
    {
      title: 'Index & Secure',
      description: 'Azure AI Search with RLS',
      icon: <Search size={16} />,
      details: status === 'completed' ? `${metadata?.chunksIndexed} chunks indexed` : null
    },
    {
      title: 'Governance Applied',
      description: 'Group-based security enforced',
      icon: <Shield size={16} />,
      details: status === 'completed' ? 'Row-Level Security Active' : null
    }
  ];

  return (
    <div className="p-6 border rounded-lg bg-white shadow-lg border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <FileText size={20} className="text-blue-600" />
          <div>
            <h3 className="font-bold text-gray-900">Ingestion Pipeline</h3>
            <p className="text-sm text-gray-600">{file}</p>
          </div>
        </div>
        
        {status === 'error' ? (
          <div className="flex items-center gap-2 text-red-600 bg-red-50 px-3 py-2 rounded-lg">
            <Shield size={16} />
            <span className="font-medium">Processing Failed</span>
          </div>
        ) : status === 'completed' ? (
          <div className="flex items-center gap-2 text-green-600 bg-green-50 px-3 py-2 rounded-lg">
            <CheckCircle size={16} />
            <span className="font-medium">Completed Successfully</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-blue-600 bg-blue-50 px-3 py-2 rounded-lg">
            <Clock size={16} />
            <span className="font-medium">Processing...</span>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {status !== 'error' && status !== 'completed' && (
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Overall Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Pipeline Steps */}
      <div className="space-y-4">
        {steps.map((step, index) => {
          const stepStatus = getStepStatus(index);
          const colorClass = getStepColor(stepStatus);
          
          return (
            <div 
              key={index}
              className={`p-4 rounded-lg border-2 transition-all duration-300 ${colorClass}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-white border-2 border-current">
                    {getStepIcon(index)}
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{step.title}</h4>
                    <p className="text-sm text-gray-600">{step.description}</p>
                  </div>
                </div>
                
                {/* Step-specific details */}
                {step.details && (
                  <div className="text-sm font-medium text-gray-700 bg-white px-2 py-1 rounded">
                    {step.details}
                  </div>
                )}
              </div>

              {/* Additional metadata for completed steps */}
              {index === 1 && status === 'completed' && metadata?.chunksCreated && (
                <div className="mt-3 pt-3 border-t border-current border-opacity-20">
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-600">Chunks Created:</span>
                    <span className="font-mono font-semibold text-blue-600">
                      {metadata.chunksCreated}
                    </span>
                    <span className="text-xs text-gray-500 italic">
                      ({parser === 'local' ? 'Layout-aware' : 'OCR-based'} chunking)
                    </span>
                  </div>
                </div>
              )}

              {index === 2 && status === 'completed' && metadata?.processingTime && (
                <div className="mt-3 pt-3 border-t border-current border-opacity-20">
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-600">Processing Time:</span>
                    <span className="font-mono font-semibold text-blue-600">
                      {(metadata.processingTime / 1000).toFixed(2)}s
                    </span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Security Information */}
      <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
        <div className="flex items-center gap-2 mb-3">
          <Lock size={16} className="text-slate-600" />
          <h4 className="font-semibold text-slate-800">Security Policy Applied</h4>
        </div>
        <div className="flex flex-wrap gap-2">
          {gids.split(',').map((gid: string, index: number) => (
            <div 
              key={gid}
              className="flex items-center gap-1 px-3 py-1 bg-slate-200 text-slate-700 rounded-md text-sm font-mono"
            >
              <Shield size={12} className="text-slate-600" />
              GID: {gid.trim()}
            </div>
          ))}
        </div>
        <div className="mt-2 text-xs text-slate-600">
          <span className="font-medium">Row-Level Security:</span> Documents accessible only to users with matching Group IDs
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 text-red-600 mb-2">
            <Shield size={16} />
            <h4 className="font-semibold">Processing Error</h4>
          </div>
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Innovation Highlights */}
      {status === 'completed' && (
        <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-2">🚀 Innovation Features Applied</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <CheckCircle size={14} className="text-green-500" />
              <span className="text-gray-700">
                {parser === 'local' ? 'IBM Docling HybridChunker' : 'Azure Document Intelligence'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle size={14} className="text-green-500" />
              <span className="text-gray-700">Layout-Aware Chunking</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle size={14} className="text-green-500" />
              <span className="text-gray-700">Table Structure Preservation</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle size={14} className="text-green-500" />
              <span className="text-gray-700">Group-Based Security</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
