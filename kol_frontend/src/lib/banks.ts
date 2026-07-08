/** Popular VietQR bin codes — KOL tự chọn ngân hàng nhận tiền của mình */
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
  { code: '970454', name: 'VietCapital / BVBank' },
  { code: '970429', name: 'SCB' },
  { code: '970414', name: 'MSB' },
  { code: '970438', name: 'BaoViet Bank' },
  { code: '970452', name: 'KienlongBank' },
  { code: '970458', name: 'UOB Vietnam' },
  { code: '970400', name: 'Saigonbank' },
  { code: '970426', name: 'Maritime Bank (MSB cũ)' },
  { code: '970425', name: 'ABBank' },
  { code: '970409', name: 'Bac A Bank' },
  { code: '970419', name: 'NCB' },
  { code: '970424', name: 'Shinhan Bank' },
  { code: '970431', name: 'Eximbank' },
  { code: '970428', name: 'Nam A Bank' },
  { code: '970440', name: 'SeABank' },
  { code: '970446', name: 'Co-opBank' },
  { code: '970449', name: 'LienVietPostBank' },
  { code: '970455', name: 'IBK - HCM' },
  { code: '970456', name: 'Indovina Bank' },
  { code: '970457', name: 'Wooribank' },
  { code: '970421', name: 'VRB' },
] as const

export function bankNameFromCode(code: string | null | undefined): string {
  if (!code) return ''
  return VN_BANKS.find((bank) => bank.code === code)?.name ?? code
}
