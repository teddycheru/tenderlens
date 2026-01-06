/**
 * Multi-step wizard for company profile setup
 * Updated to 2-step progressive onboarding with Ethiopian multi-sector business model
 */

'use client';

import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, Check, Building, Settings, AlertCircle, X } from 'lucide-react';
import {
  CompanyProfileCreateStep1,
  CompanyProfileCreateStep2,
  ProfileOptions,
  WIZARD_STEPS,
  VALIDATION,
  COMPANY_SIZES,
  YEARS_OPTIONS
} from '@/types/profile';
import { cn } from '@/lib/utils';
import { companyProfileApi } from '@/lib/company-profile';

interface ProfileSetupWizardProps {
  onComplete: (profileId: string) => void;
  onSkip?: () => void;
  initialData?: Partial<CompanyProfileCreateStep1 & CompanyProfileCreateStep2>;
}

export function ProfileSetupWizard({
  onComplete,
  onSkip,
  initialData = {}
}: ProfileSetupWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [step1Data, setStep1Data] = useState<Partial<CompanyProfileCreateStep1>>({
    primary_sector: initialData.primary_sector || '',
    active_sectors: initialData.active_sectors || [],
    sub_sectors: initialData.sub_sectors || [],
    preferred_regions: initialData.preferred_regions || [],
    keywords: initialData.keywords || []
  });
  const [step2Data, setStep2Data] = useState<Partial<CompanyProfileCreateStep2>>({
    company_size: initialData.company_size,
    years_in_operation: initialData.years_in_operation,
    certifications: initialData.certifications || [],
    budget_min: initialData.budget_min,
    budget_max: initialData.budget_max,
    budget_currency: initialData.budget_currency || 'ETB'
  });

  const [options, setOptions] = useState<ProfileOptions | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profileId, setProfileId] = useState<string | null>(null);

  // Fetch profile options on mount
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const data = await companyProfileApi.getProfileOptions();
        setOptions(data);
      } catch (err) {
        console.error('Error fetching profile options:', err);
      }
    };
    fetchOptions();
  }, []);

  const updateStep1Data = (data: Partial<CompanyProfileCreateStep1>) => {
    setStep1Data(prev => ({ ...prev, ...data }));
  };

  const updateStep2Data = (data: Partial<CompanyProfileCreateStep2>) => {
    setStep2Data(prev => ({ ...prev, ...data }));
  };

  const handleStep1Complete = async () => {
    // Validate Step 1 data
    if (!isStep1Valid()) {
      setError('Please complete all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const profile = await companyProfileApi.createProfileStep1(step1Data as CompanyProfileCreateStep1);
      setProfileId(profile.id);
      setCurrentStep(2);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to save profile';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleStep2Complete = async () => {
    setLoading(true);
    setError(null);

    try {
      const profile = await companyProfileApi.completeProfileStep2(step2Data as CompanyProfileCreateStep2);
      onComplete(profile.id);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to update profile';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSkipStep2 = () => {
    // Step 2 is optional - can skip directly to completion
    if (profileId) {
      onComplete(profileId);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const isStep1Valid = (): boolean => {
    return !!(
      step1Data.primary_sector &&
      step1Data.active_sectors &&
      step1Data.active_sectors.length >= VALIDATION.ACTIVE_SECTORS.MIN &&
      step1Data.active_sectors.length <= VALIDATION.ACTIVE_SECTORS.MAX &&
      step1Data.sub_sectors &&
      step1Data.preferred_regions &&
      step1Data.preferred_regions.length >= VALIDATION.REGIONS.MIN &&
      step1Data.keywords &&
      step1Data.keywords.length >= VALIDATION.KEYWORDS.MIN &&
      step1Data.keywords.length <= VALIDATION.KEYWORDS.MAX
    );
  };

  const StepIcon = ({ step }: { step: number }) => {
    const icons = {
      1: Building,
      2: Settings
    };
    const Icon = icons[step as keyof typeof icons];
    return <Icon className="w-5 h-5" />;
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          {WIZARD_STEPS.map((step, index) => (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center flex-1">
                <div
                  className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center mb-2 transition-colors',
                    currentStep > step.id
                      ? 'bg-green-600 text-white'
                      : currentStep === step.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  )}
                >
                  {currentStep > step.id ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    <StepIcon step={step.id} />
                  )}
                </div>
                <p className={cn(
                  'text-xs font-medium text-center',
                  currentStep === step.id ? 'text-blue-600' : 'text-gray-500'
                )}>
                  {step.title}
                </p>
              </div>
              {index < WIZARD_STEPS.length - 1 && (
                <div
                  className={cn(
                    'flex-1 h-1 mx-2 rounded',
                    currentStep > step.id ? 'bg-green-600' : 'bg-gray-200'
                  )}
                  style={{ maxWidth: '100px' }}
                />
              )}
            </React.Fragment>
          ))}
        </div>
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">
            {WIZARD_STEPS[currentStep - 1].title}
          </h2>
          <p className="text-gray-600">
            {WIZARD_STEPS[currentStep - 1].description}
          </p>
          {currentStep === 1 && (
            <p className="text-sm text-gray-500 mt-1">
              Estimated time: 45-60 seconds
            </p>
          )}
          {currentStep === 2 && (
            <p className="text-sm text-gray-500 mt-1">
              Optional • You can skip this step
            </p>
          )}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6 min-h-[500px]">
        {currentStep === 1 && (
          <Step1CriticalFields
            data={step1Data}
            options={options}
            onChange={updateStep1Data}
          />
        )}
        {currentStep === 2 && (
          <Step2Refinement
            data={step2Data}
            options={options}
            onChange={updateStep2Data}
          />
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-red-700 text-sm font-medium">Error</p>
            <p className="text-red-600 text-sm">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-400 hover:text-red-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex justify-between items-center">
        <div>
          {onSkip && currentStep === 1 && (
            <button
              onClick={onSkip}
              className="text-sm text-gray-500 hover:text-gray-700 underline"
            >
              Skip onboarding for now
            </button>
          )}
          {currentStep === 2 && (
            <button
              onClick={handleSkipStep2}
              disabled={loading}
              className="text-sm text-gray-500 hover:text-gray-700 underline disabled:opacity-50"
            >
              Skip this step
            </button>
          )}
        </div>

        <div className="flex gap-3">
          {currentStep > 1 && (
            <button
              onClick={handleBack}
              disabled={loading}
              className="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
              Back
            </button>
          )}

          <button
            onClick={currentStep === 1 ? handleStep1Complete : handleStep2Complete}
            disabled={currentStep === 1 ? !isStep1Valid() || loading : loading}
            className="inline-flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin">⏳</span>
                Saving...
              </span>
            ) : currentStep === 1 ? (
              <>
                Continue
                <ChevronRight className="w-4 h-4" />
              </>
            ) : (
              <>
                <Check className="w-4 h-4" />
                Complete Profile
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

// Step 1: Critical Fields (Required)
function Step1CriticalFields({
  data,
  options,
  onChange
}: {
  data: Partial<CompanyProfileCreateStep1>;
  options: ProfileOptions | null;
  onChange: (data: Partial<CompanyProfileCreateStep1>) => void;
}) {
  const [keywordInput, setKeywordInput] = useState('');

  const activeSectors = data.active_sectors || [];
  const keywords = data.keywords || [];
  const preferredRegions = data.preferred_regions || [];
  const subSectors = data.sub_sectors || [];

  // Get suggested keywords based on selected active sectors
  const suggestedKeywords = activeSectors.length > 0 && options?.keyword_suggestions
    ? activeSectors.flatMap(sector => options.keyword_suggestions[sector] || [])
    : [];

  const handleAddKeyword = () => {
    if (keywordInput.trim() && !keywords.includes(keywordInput.trim())) {
      if (keywords.length >= VALIDATION.KEYWORDS.MAX) {
        return; // Max keywords reached
      }
      const newKeywords = [...keywords, keywordInput.trim()];
      onChange({ keywords: newKeywords });
      setKeywordInput('');
    }
  };

  const handleRemoveKeyword = (keyword: string) => {
    onChange({ keywords: keywords.filter(k => k !== keyword) });
  };

  const handleToggleActiveSector = (sector: string) => {
    const newSectors = activeSectors.includes(sector)
      ? activeSectors.filter(s => s !== sector)
      : activeSectors.length < VALIDATION.ACTIVE_SECTORS.MAX
        ? [...activeSectors, sector]
        : activeSectors; // Max reached
    onChange({ active_sectors: newSectors });
  };

  const handleToggleRegion = (region: string) => {
    const newRegions = preferredRegions.includes(region)
      ? preferredRegions.filter(r => r !== region)
      : preferredRegions.length < VALIDATION.REGIONS.MAX
        ? [...preferredRegions, region]
        : preferredRegions; // Max reached
    onChange({ preferred_regions: newRegions });
  };

  const handleToggleSubSector = (sector: string) => {
    const newSubSectors = subSectors.includes(sector)
      ? subSectors.filter(s => s !== sector)
      : [...subSectors, sector];
    onChange({ sub_sectors: newSubSectors });
  };

  return (
    <div className="space-y-6">
      {/* Primary Sector - Identity */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          What sector do you primarily identify as? <span className="text-red-500">*</span>
        </label>
        <p className="text-xs text-gray-500 mb-3">
          This is for branding and identity - the sector people associate with your company
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {options?.sectors.map(sector => (
            <label
              key={sector}
              className={cn(
                'flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors',
                data.primary_sector === sector
                  ? 'bg-blue-50 border-blue-500 ring-2 ring-blue-200'
                  : 'hover:bg-gray-50 border-gray-200'
              )}
            >
              <input
                type="radio"
                name="primary_sector"
                value={sector}
                checked={data.primary_sector === sector}
                onChange={(e) => onChange({ primary_sector: e.target.value })}
                className="text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium">{sector}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Active Sectors - Actual Work */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          What sectors do you actively work in? <span className="text-red-500">*</span>
        </label>
        <p className="text-xs text-gray-500 mb-3">
          Select sectors you bid on and win contracts in. You can select up to {VALIDATION.ACTIVE_SECTORS.MAX}.
          <span className="font-medium ml-1">
            ({activeSectors.length}/{VALIDATION.ACTIVE_SECTORS.MAX} selected)
          </span>
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-60 overflow-y-auto p-2 border rounded-lg">
          {options?.sectors.map(sector => (
            <label
              key={sector}
              className={cn(
                'flex items-center gap-2 p-2 rounded cursor-pointer transition-colors',
                activeSectors.includes(sector)
                  ? 'bg-green-50'
                  : 'hover:bg-gray-50',
                activeSectors.length >= VALIDATION.ACTIVE_SECTORS.MAX && !activeSectors.includes(sector)
                  ? 'opacity-50 cursor-not-allowed'
                  : ''
              )}
            >
              <input
                type="checkbox"
                checked={activeSectors.includes(sector)}
                onChange={() => handleToggleActiveSector(sector)}
                disabled={activeSectors.length >= VALIDATION.ACTIVE_SECTORS.MAX && !activeSectors.includes(sector)}
                className="rounded text-green-600 focus:ring-green-500"
              />
              <span className="text-sm">{sector}</span>
            </label>
          ))}
        </div>
        {activeSectors.length >= VALIDATION.ACTIVE_SECTORS.MAX && (
          <p className="text-xs text-amber-600 mt-2">
            Maximum sectors reached. Deselect one to choose another.
          </p>
        )}
      </div>

      {/* Sub-Sectors */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Any specific specializations? (optional but recommended)
        </label>
        <p className="text-xs text-gray-500 mb-3">
          Fine-grained specializations help us focus on the most relevant tenders
        </p>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            placeholder="e.g., Road Construction, Web Development, Medical Equipment..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                const value = e.currentTarget.value.trim();
                if (value && !subSectors.includes(value)) {
                  handleToggleSubSector(value);
                  e.currentTarget.value = '';
                }
              }
            }}
          />
        </div>
        {subSectors.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {subSectors.map(sector => (
              <span
                key={sector}
                className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm flex items-center gap-1"
              >
                {sector}
                <button
                  onClick={() => handleToggleSubSector(sector)}
                  className="hover:text-indigo-900"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Preferred Regions */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Preferred Regions <span className="text-red-500">*</span>
        </label>
        <p className="text-xs text-gray-500 mb-3">
          Select up to {VALIDATION.REGIONS.MAX} regions where you prefer to work.
          <span className="font-medium ml-1">
            ({preferredRegions.length}/{VALIDATION.REGIONS.MAX} selected)
          </span>
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 p-3 border rounded-lg">
          {options?.regions.map(region => (
            <label
              key={region}
              className={cn(
                'flex items-center gap-2 p-2 rounded cursor-pointer transition-colors',
                preferredRegions.includes(region)
                  ? 'bg-blue-50'
                  : 'hover:bg-gray-50',
                preferredRegions.length >= VALIDATION.REGIONS.MAX && !preferredRegions.includes(region)
                  ? 'opacity-50 cursor-not-allowed'
                  : ''
              )}
            >
              <input
                type="checkbox"
                checked={preferredRegions.includes(region)}
                onChange={() => handleToggleRegion(region)}
                disabled={preferredRegions.length >= VALIDATION.REGIONS.MAX && !preferredRegions.includes(region)}
                className="rounded text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm">{region}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Keywords */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Core Keywords <span className="text-red-500">*</span>
        </label>
        <p className="text-xs text-gray-500 mb-3">
          Add {VALIDATION.KEYWORDS.MIN}-{VALIDATION.KEYWORDS.MAX} keywords describing your core capabilities.
          <span className="font-medium ml-1">
            ({keywords.length}/{VALIDATION.KEYWORDS.MAX})
          </span>
        </p>

        {/* Suggested Keywords */}
        {suggestedKeywords.length > 0 && (
          <div className="mb-3">
            <p className="text-xs text-gray-600 mb-2">Suggested based on your sectors:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedKeywords.slice(0, 12).map(keyword => (
                <button
                  key={keyword}
                  onClick={() => {
                    if (!keywords.includes(keyword) && keywords.length < VALIDATION.KEYWORDS.MAX) {
                      onChange({ keywords: [...keywords, keyword] });
                    }
                  }}
                  disabled={keywords.includes(keyword) || keywords.length >= VALIDATION.KEYWORDS.MAX}
                  className={cn(
                    'px-3 py-1 rounded-full text-sm border transition-colors',
                    keywords.includes(keyword)
                      ? 'bg-blue-100 border-blue-300 text-blue-700 cursor-not-allowed'
                      : keywords.length >= VALIDATION.KEYWORDS.MAX
                        ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
                        : 'bg-white border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                  )}
                >
                  {keyword}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Custom Keyword Input */}
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
            placeholder="Add custom keyword..."
            disabled={keywords.length >= VALIDATION.KEYWORDS.MAX}
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none disabled:bg-gray-100 text-sm"
          />
          <button
            onClick={handleAddKeyword}
            disabled={keywords.length >= VALIDATION.KEYWORDS.MAX}
            className="px-4 py-2 bg-blue-100 rounded-lg hover:bg-blue-200 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            Add
          </button>
        </div>

        {/* Selected Keywords */}
        {keywords.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {keywords.map(keyword => (
              <span
                key={keyword}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-1 font-medium"
              >
                {keyword}
                <button
                  onClick={() => handleRemoveKeyword(keyword)}
                  className="hover:text-blue-900"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Validation Messages */}
        {keywords.length < VALIDATION.KEYWORDS.MIN && (
          <p className="text-xs text-amber-600 mt-2">
            Add at least {VALIDATION.KEYWORDS.MIN - keywords.length} more keyword(s)
          </p>
        )}
        {keywords.length >= VALIDATION.KEYWORDS.MAX && (
          <p className="text-xs text-green-600 mt-2">
            Maximum keywords reached
          </p>
        )}
      </div>

      {/* Progress Indicator */}
      <div className="pt-4 border-t">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-600">Profile Completion</span>
          <span className="font-medium text-gray-900">
            {[
              !!data.primary_sector,
              activeSectors.length >= VALIDATION.ACTIVE_SECTORS.MIN,
              preferredRegions.length >= VALIDATION.REGIONS.MIN,
              keywords.length >= VALIDATION.KEYWORDS.MIN
            ].filter(Boolean).length} / 4 required fields
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{
              width: `${([
                !!data.primary_sector,
                activeSectors.length >= VALIDATION.ACTIVE_SECTORS.MIN,
                preferredRegions.length >= VALIDATION.REGIONS.MIN,
                keywords.length >= VALIDATION.KEYWORDS.MIN
              ].filter(Boolean).length / 4) * 100}%`
            }}
          />
        </div>
      </div>
    </div>
  );
}

// Step 2: Refinement (Optional)
function Step2Refinement({
  data,
  options,
  onChange
}: {
  data: Partial<CompanyProfileCreateStep2>;
  options: ProfileOptions | null;
  onChange: (data: Partial<CompanyProfileCreateStep2>) => void;
}) {
  const [customCertification, setCustomCertification] = useState('');
  const certifications = data.certifications || [];

  const handleToggleCertification = (cert: string) => {
    const newCerts = certifications.includes(cert)
      ? certifications.filter(c => c !== cert)
      : [...certifications, cert];
    onChange({ certifications: newCerts });
  };

  const handleAddCustomCertification = () => {
    if (customCertification.trim() && !certifications.includes(customCertification.trim())) {
      onChange({ certifications: [...certifications, customCertification.trim()] });
      setCustomCertification('');
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-800">
          <strong>These fields are optional</strong> but help improve recommendation precision.
          You can skip this step and your profile will still work great!
        </p>
      </div>

      {/* Company Size */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Company Size
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {COMPANY_SIZES.map(size => (
            <label
              key={size.value}
              className={cn(
                'flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors',
                data.company_size === size.value
                  ? 'bg-blue-50 border-blue-500 ring-2 ring-blue-200'
                  : 'hover:bg-gray-50 border-gray-200'
              )}
            >
              <input
                type="radio"
                name="company_size"
                value={size.value}
                checked={data.company_size === size.value}
                onChange={(e) => onChange({ company_size: e.target.value })}
                className="text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm">{size.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Years in Operation */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Years in Operation
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {YEARS_OPTIONS.map(option => (
            <label
              key={option.value}
              className={cn(
                'flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors',
                data.years_in_operation === option.value
                  ? 'bg-blue-50 border-blue-500 ring-2 ring-blue-200'
                  : 'hover:bg-gray-50 border-gray-200'
              )}
            >
              <input
                type="radio"
                name="years_in_operation"
                value={option.value}
                checked={data.years_in_operation === option.value}
                onChange={(e) => onChange({ years_in_operation: e.target.value })}
                className="text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm">{option.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Certifications */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Certifications
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
          {options?.certifications.map(cert => (
            <label
              key={cert}
              className={cn(
                'flex items-center gap-2 p-2 rounded cursor-pointer transition-colors',
                certifications.includes(cert) ? 'bg-green-50' : 'hover:bg-gray-50'
              )}
            >
              <input
                type="checkbox"
                checked={certifications.includes(cert)}
                onChange={() => handleToggleCertification(cert)}
                className="rounded text-green-600 focus:ring-green-500"
              />
              <span className="text-sm">{cert}</span>
            </label>
          ))}
        </div>

        {/* Custom Certification */}
        <div className="flex gap-2">
          <input
            type="text"
            value={customCertification}
            onChange={(e) => setCustomCertification(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddCustomCertification()}
            placeholder="Add other certification..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm"
          />
          <button
            onClick={handleAddCustomCertification}
            className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Add
          </button>
        </div>

        {/* Custom Certifications Display */}
        {certifications.some(c => !options?.certifications.includes(c)) && (
          <div className="flex flex-wrap gap-2 mt-2">
            {certifications
              .filter(c => !options?.certifications.includes(c))
              .map(cert => (
                <span
                  key={cert}
                  className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm flex items-center gap-1"
                >
                  {cert}
                  <button
                    onClick={() => handleToggleCertification(cert)}
                    className="hover:text-purple-900"
                  >
                    ×
                  </button>
                </span>
              ))}
          </div>
        )}
      </div>

      {/* Budget Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Typical Project Budget Range
        </label>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-600 mb-1">Minimum (ETB)</label>
            <input
              type="number"
              value={data.budget_min || ''}
              onChange={(e) => onChange({ budget_min: parseFloat(e.target.value) || undefined })}
              placeholder="e.g., 50000"
              min="0"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">Maximum (ETB)</label>
            <input
              type="number"
              value={data.budget_max || ''}
              onChange={(e) => onChange({ budget_max: parseFloat(e.target.value) || undefined })}
              placeholder="e.g., 5000000"
              min="0"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          This helps us prioritize tenders within your capacity
        </p>
      </div>

      {/* Completion Summary */}
      <div className="pt-4 border-t">
        <p className="text-sm text-gray-600">
          <strong>
            {[
              !!data.company_size,
              !!data.years_in_operation,
              certifications.length > 0,
              !!(data.budget_min && data.budget_max)
            ].filter(Boolean).length} of 4
          </strong>{' '}
          optional fields completed
        </p>
      </div>
    </div>
  );
}
