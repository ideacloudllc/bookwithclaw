interface ModalProps {
  isOpen: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

export const Modal = ({ isOpen, title, onClose, children, actions }: ModalProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-bold">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            ×
          </button>
        </div>
        <div className="px-6 py-4">{children}</div>
        {actions && <div className="border-t px-6 py-3 flex gap-3 justify-end">{actions}</div>}
      </div>
    </div>
  );
};
