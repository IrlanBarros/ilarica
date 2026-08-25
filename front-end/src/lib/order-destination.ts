export function formatDeliveryDestination(
  destination: { name: string } | null,
  locationDetails: string | null | undefined,
): string {
  const zoneName = destination?.name ?? 'Indisponível';
  const normalizedDetails = locationDetails?.trim();
  return normalizedDetails ? `${zoneName} - ${normalizedDetails}` : zoneName;
}