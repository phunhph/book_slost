export const VN_BANKS = [
  { code: '970436', name: 'Vietcombank (VCB)' },
  { code: '970415', name: 'VietinBank' },
  { code: '970418', name: 'BIDV' },
  { code: '970405', name: 'Agribank' },
  { code: '970422', name: 'MB Bank' },
  { code: '970407', name: 'Techcombank' },
  { code: '970432', name: 'VPBank' },
  { code: '970423', name: 'TPBank' },
  { code: '970403', name: 'Sacombank' },
  { code: '970448', name: 'OCB' },
  { code: '970437', name: 'HDBank' },
  { code: '970441', name: 'VIB' },
  { code: '970443', name: 'SHB' },
  { code: '970454', name: 'VietCapital Bank' },
  { code: '970429', name: 'SCB' },
  { code: '970414', name: 'MSB' },
  { code: '970438', name: 'BaoViet Bank' },
  { code: '970452', name: 'KienlongBank' },
  { code: '970458', name: 'UOB Vietnam' },
  { code: '970400', name: 'Saigonbank' },
] as const

export function bankNameFromCode(code: string | null | undefined): string {
  if (!code) return ''
  return VN_BANKS.find((bank) => bank.code === code)?.name ?? code
}
