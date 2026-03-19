interface FormInputProps {
  label: string;
  name: string;
  type?: string;
  value: string;
  onChange: (e: any) => void;
  error?: string;
  required?: boolean;
  placeholder?: string;
  multiline?: boolean;
  rows?: number;
}

export const FormInput = ({
  label,
  name,
  type = 'text',
  value,
  onChange,
  error,
  required = false,
  placeholder,
  multiline = false,
  rows = 3,
}: FormInputProps) => {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {multiline ? (
        <textarea
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          rows={rows}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
            error ? 'border-red-500' : 'border-gray-300'
          }`}
        />
      ) : (
        <input
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            error ? 'border-red-500' : 'border-gray-300'
          }`}
        />
      )}
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  );
};
