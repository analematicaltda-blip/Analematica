export const contableMapper = {
  mapAccountToUI: (acc: any) => ({
    id: acc.id || acc.code,
    code: acc.code,
    name: acc.name,
    type: acc.nature,
    balance: `$${parseFloat(acc.balance || 0).toLocaleString()}`,
    color: acc.nature === 'DEBITO' ? 'green' : 'red'
  }),

  mapAsientoToUI: (entry: any) => ({
    id: entry.id,
    date: new Date(entry.entry_date).toLocaleDateString(),
    description: entry.description,
    total: `$${parseFloat(entry.total_amount || 0).toLocaleString()}`,
    type: entry.entry_type
  })
};
