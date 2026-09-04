export function Button({ variant = 'primary', className = '', ...props }) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
  const variants = {
    primary: 'bg-marigold text-white hover:bg-marigold-dark',
    secondary: 'bg-white text-ink border border-sand hover:bg-paper',
    danger: 'bg-clay text-white hover:bg-clay/90',
    ghost: 'text-slate hover:text-ink hover:bg-paper',
  }
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />
}

export function Input({ label, error, className = '', ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1.5 block text-sm font-medium text-ink">{label}</span>}
      <input
        className={`w-full rounded-md border border-sand bg-white px-3 py-2 text-sm text-ink placeholder:text-slate/60 focus:border-marigold ${className}`}
        {...props}
      />
      {error && <span className="mt-1 block text-xs text-clay">{error}</span>}
    </label>
  )
}

export function Textarea({ label, className = '', ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1.5 block text-sm font-medium text-ink">{label}</span>}
      <textarea
        className={`w-full rounded-md border border-sand bg-white px-3 py-2 text-sm text-ink placeholder:text-slate/60 focus:border-marigold ${className}`}
        {...props}
      />
    </label>
  )
}

export function Select({ label, className = '', children, ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1.5 block text-sm font-medium text-ink">{label}</span>}
      <select
        className={`w-full rounded-md border border-sand bg-white px-3 py-2 text-sm text-ink focus:border-marigold ${className}`}
        {...props}
      >
        {children}
      </select>
    </label>
  )
}

export function Checkbox({ label, ...props }) {
  return (
    <label className="flex items-center gap-2 text-sm text-ink">
      <input type="checkbox" className="h-4 w-4 rounded border-sand accent-marigold" {...props} />
      {label}
    </label>
  )
}

export function Badge({ children, tone = 'default' }) {
  const tones = {
    default: 'bg-sand text-ink',
    success: 'bg-moss-light text-moss',
    danger: 'bg-clay/10 text-clay',
    accent: 'bg-marigold-light text-marigold-dark',
  }
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${tones[tone]}`}>
      {children}
    </span>
  )
}

export function Card({ children, className = '' }) {
  return <div className={`rounded-lg border border-sand bg-white ${className}`}>{children}</div>
}

export function EmptyState({ title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-sand py-16 text-center">
      <p className="text-base font-medium text-ink">{title}</p>
      {description && <p className="mt-1 max-w-sm text-sm text-slate">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
