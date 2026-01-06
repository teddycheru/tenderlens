// @ts-nocheck

import React, { useState } from 'react';
import { CompanyProfileCreate, ProfileOptions } from '@/types/profile';
import { CheckCircle } from 'lucide-react';

// Step 2: Capabilities & Qualifications
export function Step2Capabilities({
  data,
  options,
  onChange
}: {
  data: Partial<CompanyProfileCreate>;
  options: ProfileOptions | null;
  onChange: (data: Partial<CompanyProfileCreate>) => void;
}) {
  const [capabilityInput, setCapabilityInput] = useState('');
  const [expertiseInput, setExpertiseInput] = useState('');

  const handleAddCapability = () => {
    if (capabilityInput.trim()) {
      // const current = data.technical_capabilities || [];
      // onChange({ technical_capabilities: [...current, capabilityInput.trim()] });
      // setCapabilityInput('');
    }
  };

  const handleAddExpertise = () => {
    if (expertiseInput.trim()) {
      const current = data.team_expertise || [];
      onChange({ team_expertise: [...current, expertiseInput.trim()] });
      setExpertiseInput('');
    }
  };

  return (
    <div className="space-y-6">
      {/* Certifications */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Certifications
        </label>
        <div className="grid grid-cols-2 gap-2 p-3 border rounded-lg max-h-48 overflow-y-auto">
          {options?.certifications.map(cert => (
            <label key={cert} className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
              <input
                type="checkbox"
                checked={(data.certifications || []).includes(cert)}
                onChange={(e) => {
                  const current = data.certifications || [];
                  const newCerts = e.target.checked
                    ? [...current, cert]
                    : current.filter(c => c !== cert);
                  onChange({ certifications: newCerts });
                }}
                className="rounded"
              />
              <span className="text-sm">{cert}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Past Project Types */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Past Project Types
        </label>
        <div className="flex flex-wrap gap-2 p-3 border rounded-lg">
          {options?.project_types.map(type => (
            <button
              key={type}
              onClick={() => {
                const current = data.past_project_types || [];
                const newTypes = current.includes(type)
                  ? current.filter(t => t !== type)
                  : [...current, type];
                onChange({ past_project_types: newTypes });
              }}
              className={`px-4 py-2 rounded-lg text-sm border transition-colors ${
                (data.past_project_types || []).includes(type)
                  ? 'bg-blue-100 border-blue-300 text-blue-700'
                  : 'bg-gray-50 border-gray-200 hover:border-gray-300'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Technical Capabilities */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Technical Capabilities
        </label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={capabilityInput}
            onChange={(e) => setCapabilityInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddCapability()}
            placeholder="e.g. ERP implementation, Cloud infrastructure..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
          <button
            onClick={handleAddCapability}
            className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Add
          </button>
        </div>
        {(data.technical_capabilities || []).length > 0 && (
          <div className="flex flex-wrap gap-2">
            {data.technical_capabilities!.map((cap, idx) => (
              <span key={idx} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm flex items-center gap-1">
                {cap}
                <button
                  onClick={() => {
                    const newCaps = data.technical_capabilities!.filter((_, i) => i !== idx);
                    onChange({ technical_capabilities: newCaps });
                  }}
                  className="hover:text-green-900"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Team Expertise */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Team Expertise Areas
        </label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={expertiseInput}
            onChange={(e) => setExpertiseInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddExpertise()}
            placeholder="e.g. Project Management, Software Development..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
          <button
            onClick={handleAddExpertise}
            className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Add
          </button>
        </div>
        {(data.team_expertise || []).length > 0 && (
          <div className="flex flex-wrap gap-2">
            {data.team_expertise!.map((exp, idx) => (
              <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm flex items-center gap-1">
                {exp}
                <button
                  onClick={() => {
                    const newExp = data.team_expertise!.filter((_, i) => i !== idx);
                    onChange({ team_expertise: newExp });
                  }}
                  className="hover:text-purple-900"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Step 3: Tender Preferences
export function Step3Preferences({
  data,
  options,
  onChange
}: {
  data: Partial<CompanyProfileCreate>;
  options: ProfileOptions | null;
  onChange: (data: Partial<CompanyProfileCreate>) => void;
}) {
  return (
    <div className="space-y-6">
      {/* Preferred Regions */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Preferred Regions
        </label>
        <div className="grid grid-cols-3 gap-2 p-3 border rounded-lg max-h-48 overflow-y-auto">
          {options?.regions.map(region => (
            <label key={region} className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
              <input
                type="checkbox"
                checked={(data.preferred_regions || []).includes(region)}
                onChange={(e) => {
                  const current = data.preferred_regions || [];
                  const newRegions = e.target.checked
                    ? [...current, region]
                    : current.filter(r => r !== region);
                  onChange({ preferred_regions: newRegions });
                }}
                className="rounded"
              />
              <span className="text-sm">{region}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Budget Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Budget Range (ETB)
        </label>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <input
              type="number"
              value={data.budget_min || ''}
              onChange={(e) => onChange({ budget_min: parseFloat(e.target.value) || undefined })}
              placeholder="Minimum budget"
              min="0"
              step="1000"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <input
              type="number"
              value={data.budget_max || ''}
              onChange={(e) => onChange({ budget_max: parseFloat(e.target.value) || undefined })}
              placeholder="Maximum budget"
              min="0"
              step="1000"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Leave empty to see all tenders regardless of budget
        </p>
      </div>

      {/* Preferred Languages */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Preferred Languages
        </label>
        <div className="flex flex-wrap gap-2 p-3 border rounded-lg">
          {options?.languages.map(lang => (
            <button
              key={lang}
              onClick={() => {
                const current = data.preferred_languages || [];
                const newLangs = current.includes(lang)
                  ? current.filter(l => l !== lang)
                  : [...current, lang];
                onChange({ preferred_languages: newLangs });
              }}
              className={`px-4 py-2 rounded-lg text-sm border transition-colors ${
                (data.preferred_languages || []).includes(lang)
                  ? 'bg-blue-100 border-blue-300 text-blue-700'
                  : 'bg-gray-50 border-gray-200 hover:border-gray-300'
              }`}
            >
              {lang}
            </button>
          ))}
        </div>
      </div>

      {/* Minimum Deadline Days */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Minimum Days Before Deadline
        </label>
        <input
          type="number"
          value={data.min_deadline_days ?? 7}
          onChange={(e) => onChange({ min_deadline_days: parseInt(e.target.value) || 7 })}
          min="0"
          max="90"
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
        <p className="text-xs text-gray-500 mt-1">
          Only show tenders with at least this many days remaining
        </p>
      </div>

      {/* Minimum Match Threshold */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Minimum Match Score: {data.min_match_threshold ?? 50}%
        </label>
        <input
          type="range"
          value={data.min_match_threshold ?? 50}
          onChange={(e) => onChange({ min_match_threshold: parseInt(e.target.value) })}
          min="0"
          max="100"
          step="5"
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>0% (Show all)</span>
          <span>100% (Perfect match only)</span>
        </div>
      </div>
    </div>
  );
}

// Step 4: Review & Confirm
export function Step4Review({
  data,
  options
}: {
  data: Partial<CompanyProfileCreate>;
  options: ProfileOptions | null;
}) {
  const sections = [
    {
      title: 'Business Identity',
      items: [
        { label: 'Primary Sector', value: data.primary_sector },
        { label: 'Specializations', value: data.sub_sectors?.join(', ') },
        { label: 'Keywords', value: [...(data.predefined_keywords || []), ...(data.custom_keywords || [])].join(', ') },
        { label: 'Company Size', value: data.company_size },
        { label: 'Years in Operation', value: data.years_in_operation }
      ]
    },
    {
      title: 'Capabilities',
      items: [
        { label: 'Certifications', value: data.certifications?.join(', ') },
        { label: 'Past Projects', value: data.past_project_types?.join(', ') },
        { label: 'Technical Capabilities', value: data.technical_capabilities?.join(', ') },
        { label: 'Team Expertise', value: data.team_expertise?.join(', ') }
      ]
    },
    {
      title: 'Preferences',
      items: [
        { label: 'Preferred Regions', value: data.preferred_regions?.join(', ') },
        { label: 'Budget Range', value: data.budget_min && data.budget_max ? `${data.budget_min.toLocaleString()} - ${data.budget_max.toLocaleString()} ETB` : undefined },
        { label: 'Languages', value: data.preferred_languages?.join(', ') },
        { label: 'Min. Deadline Days', value: data.min_deadline_days },
        { label: 'Min. Match Score', value: `${data.min_match_threshold ?? 50}%` }
      ]
    }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-medium text-blue-900">Profile Ready!</h3>
            <p className="text-sm text-blue-700 mt-1">
              Review your profile below. You can always update it later in settings.
            </p>
          </div>
        </div>
      </div>

      {sections.map(section => (
        <div key={section.title} className="border rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-3">{section.title}</h3>
          <div className="space-y-2">
            {section.items.map(item => (
              item.value ? (
                <div key={item.label} className="flex">
                  <span className="text-sm text-gray-600 w-40 flex-shrink-0">{item.label}:</span>
                  <span className="text-sm text-gray-900 flex-1">{item.value}</span>
                </div>
              ) : null
            ))}
          </div>
        </div>
      ))}

      {data.company_description && (
        <div className="border rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Company Description</h3>
          <p className="text-sm text-gray-700">{data.company_description}</p>
        </div>
      )}
    </div>
  );
}
