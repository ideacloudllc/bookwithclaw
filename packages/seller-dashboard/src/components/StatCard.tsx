interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'purple' | 'orange';
}

const colorClasses = {
  blue: 'bg-blue-50 text-blue-600 border-blue-200',
  green: 'bg-green-50 text-green-600 border-green-200',
  purple: 'bg-purple-50 text-purple-600 border-purple-200',
  orange: 'bg-orange-50 text-orange-600 border-orange-200',
};

export const StatCard = ({ label, value, icon, color = 'blue' }: StatCardProps) => {
  return (
    <div className={`border rounded-lg p-6 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-75">{label}</p>
          <p className="text-2xl font-bold mt-2">{value}</p>
        </div>
        {icon && <div className="text-3xl opacity-50">{icon}</div>}
      </div>
    </div>
  );
};
