// Catalog agent (war room): the catalog team's corrections and the per-SKU mapping cache.
// The Runtime reads and writes them (infra/sst/runtime.ts); scripts/correct.sh loads
// corrections from a laptop with the SSO profile.
export const correctionsTable = new sst.aws.Dynamo("CatalogCorrections", {
  fields: { category_urn: "string", correction_key: "string" },
  primaryIndex: { hashKey: "category_urn", rangeKey: "correction_key" },
});

export const mappingCacheTable = new sst.aws.Dynamo("CatalogMappingCache", {
  fields: { product_key: "string", version_key: "string" },
  primaryIndex: { hashKey: "product_key", rangeKey: "version_key" },
});
