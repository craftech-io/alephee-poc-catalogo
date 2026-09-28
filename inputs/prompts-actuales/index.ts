import { Language } from '@alephee/core-shared';
import { CatalogItem } from '@this/models/catalog.item';

export const categoryPrompt = (product: CatalogItem, categories: any, language: string): string => `
You are an assistant that must identify the single best matching marketplace category
for a given CRM product.

Follow these steps carefully:

1️⃣ Step 1 — Exact Match:
- Compare the CRM category name with each marketplace category name.
- If you find an **exact or nearly identical** match (ignoring case, accents, plural/singular),
  return that category immediately.

2️⃣ Step 2 — Semantic Match:
- Only if no exact match exists, choose the category whose meaning is most related
  to both the CRM category name and the product name.

3️⃣ Rules:
- Never invent, merge, or rename categories.
- Never modify the URN. You must copy it **exactly as shown** in the list below, including the full prefix like "urn:category:..."
- The output must be **valid JSON only**, with this exact structure:
{
  "urn": "Category_Urn",
  "name": "Category_Name"
}

CRM Category: "${product.categories?.[0].name}"
Product Name: "${product.name}"
Output language: ${Language.getLanguageName(language)}

Marketplace Categories (list):
${categories.map((c: any) => `- ${c.name} (${c.urn})`).join('\n')}

Example:
If CRM Category = "Capas para Bancos" and marketplace categories include one named "Capas para Bancos" with urn "urn:category:738612:vendor:bees",
then output exactly:
{
  "urn": "urn:category:738612:vendor:bees",
  "name": "Capas para Bancos"
}
`;

export const attributeReferencePrompt = (
  product: CatalogItem,
  attributes: any,
  referenceAttributes: any,
): string => `
**TASK**

Generate a JSON response with a single root field:

{
  "data": []
}

IMPORTANT:
- Return ONLY valid JSON
- Do NOT explain
- Do NOT add markdown

--------------------------------------------------
REFERENCE ATTRIBUTE PROCESSING
--------------------------------------------------

REFERENCE ATTRIBUTES:
${JSON.stringify(referenceAttributes)}

PRODUCT ATTRIBUTES:
${JSON.stringify(product.attributes)}

EXTERNAL ATTRIBUTES:
${JSON.stringify(attributes)}

Rules:

A match exists when the product attribute id equals REFERENCE ATTRIBUTE legacyId.

How to extract the product attribute id from PRODUCT ATTRIBUTE urn:
- Take the id segment after "urn:attribute:"
- Stop before the next ":" if present
- Examples:
  - "urn:attribute:1673" → "1673"
  - "urn:attribute:1673:vendor:shopee" → "1673"

Compare as strings:
- String(REFERENCE ATTRIBUTE.legacyId) == product attribute id

Also accept an exact full-urn equality fallback:
- PRODUCT ATTRIBUTE urn == REFERENCE ATTRIBUTE legacyId

For each REFERENCE ATTRIBUTE:

1. Find PRODUCT ATTRIBUTE using the match rules above.

2. If no match exists:
   - Skip

3. If match exists:
   - Include the attribute

Output rules:

- urn:
  MUST be copied EXACTLY from REFERENCE ATTRIBUTE urn.
  That urn already includes the vendor scope (":vendor:...").

- name:
  If an external attribute exists with the same urn as REFERENCE ATTRIBUTE urn:
    Use the external attribute name.
  Otherwise:
    Use REFERENCE ATTRIBUTE name.

- type:

  1. Find the external attribute whose urn matches REFERENCE ATTRIBUTE urn.

  2. If found:
     Use the external attribute type.

  3. If not found:
     Use "FREE_TEXT_FIELD".

- values:

  Use ONLY the value of the PRODUCT ATTRIBUTE matched in step 1.
  Never reuse another product attribute value.

  1. If that PRODUCT ATTRIBUTE has no value:
     Skip the attribute

  2. Find the external attribute whose urn matches REFERENCE ATTRIBUTE urn.

  3. If the external attribute contains a non-empty predefined values list:

     - Select the closest matching external value by name/display.
     - Output MUST use that external value id and name.
     - If no close match exists among predefined values: Skip the attribute.
     - NEVER output id "0" when predefined values exist.

     Example:

     Product value:
     "Novo"

     External value:
     {
       "id": "2497",
       "name": "Novo"
     }

     Output:

     [
       {
         "id": "2497",
         "name": "Novo"
       }
     ]

  4. If the external attribute does not contain predefined values (free text):

     [
       {
         "id": "0",
         "name": "<matched product value>"
       }
     ]

Important:

- NEVER use PRODUCT ATTRIBUTE urn as output urn
- NEVER use legacyId as output urn
- NEVER invent urns
- NEVER strip or rewrite ":vendor:..." from REFERENCE ATTRIBUTE urn
- NEVER copy one product value onto unrelated attributes
- NEVER transform units
- Use external attribute type when available.
- Prefer skipping over inventing a value match.

Output:

{
  "data": [
    {
      "urn": "...",
      "name": "...",
      "type": "FREE_TEXT_FIELD",
      "values": [...]
    }
  ]
}
`;

export const attributePrompt = (
  product: CatalogItem,
  attributes: any,
  language: string,
  vendor: string,
): string => `
**Task:**
TASK

Generate a JSON response with a single root field:

{
  "data": []
}

IMPORTANT:
- Return ONLY valid JSON
- Do NOT explain
- Do NOT add markdown

--------------------------------------------------
ATTRIBUTE MAPPING
--------------------------------------------------

Map CRM attributes to external attributes.

CRM Attributes:
${JSON.stringify(product.attributes)}

External Attributes:
${JSON.stringify(attributes)}

Adapter:
${vendor}

Language:
${language}

Category:
${product.categories?.[0].name}

Rules:

- Include only attributes that have a close match between CRM and external attributes.
- Each CRM attribute may map to at most one external attribute.
- Each external attribute (urn) may appear only once.
- Prefer fewer high-confidence mappings over many weak ones.
- Never invent attributes.
- Never create new external urns.
- If no valid match exists, skip.
- Output urn MUST be copied EXACTLY from an External Attributes item.
- Output urn MUST include ":vendor:${vendor}".
- NEVER use a CRM/product attribute urn as output urn.
- NEVER emit urns like "urn:attribute:1673" without vendor scope.

Matching priority (for choosing which EXTERNAL attribute to keep):

1. Exact name match between CRM attribute name and external attribute name/display
2. Strong semantic similarity between the same CRM attribute and one external attribute
3. Do NOT reuse CRM attribute ids as output urns, even if numbers look similar
4. Do NOT map one CRM attribute (for example Condition/"Novo") onto unrelated external attributes (Material, Style, Pattern, etc.)

Values:

- Output values MUST come only from the specifically matched CRM attribute.
- NEVER copy the same CRM value to multiple external attributes unless those CRM attributes are different matches.
- If external attribute contains a non-empty predefined values list:
  - Choose the closest matching predefined value by name/display.
  - Use that external value id and name.
  - If no close match exists: SKIP the attribute.
  - NEVER output id "0" when predefined values exist.
- If external attribute does not contain predefined values (free text):
  - Use:

  {
    "id": "0",
    "name": "<matched crm value>"
  }

Units:

- If CRM contains a unit:
  - Use the closest available unit from the external attribute.

- If no compatible unit exists:
  - Skip the attribute.

--------------------------------------------------
TYPE RULES
--------------------------------------------------

If adapter = "shopee":

Allowed types:

- SINGLE_DROP_DOWN
- SINGLE_COMBO_BOX
- FREE_TEXT_FIELD
- MULTI_DROP_DOWN
- MULTI_COMBO_BOX

If external type is different:

- Text-like -> FREE_TEXT_FIELD
- Single option -> SINGLE_DROP_DOWN
- Multiple options -> MULTI_DROP_DOWN

If no reasonable mapping exists:
- Skip

If type cannot be inferred:
- FREE_TEXT_FIELD

For non-shopee adapters:

- Use external type.
- If missing, use "string".

--------------------------------------------------
OUTPUT
--------------------------------------------------

{
  "data": [
    {
      "urn": "urn:attribute:<external-id>:vendor:${vendor}",
      "name": "...",
      "type": "...",
      "values": [
        {
          "id": "...",
          "name": "...",
          "unit": "..."
        }
      ]
    }
  ]
}
`;

export const brandPrompt = (
  product: CatalogItem,
  brands: any,
): string => `Identify the closest marketplace brand that matches the given CRM brand and product name. The CRM details are:
    - Brand Name: ${product?.brand?.[0]?.name}.
    - Product Name: ${product.name}.
    - Note that you are cataloging an auto parts related product.
    Marketplace brands are provided in the following JSON: ${JSON.stringify(brands)}.
    Please return only the most relevant marketplace brand ID and brand name in JSON format, following this structure:
    {
    "id": "Brand_urn",
    "name": "Brand_Name"
    }
    if not match found, the marketplace provide one option without brand.
    `;

export const productInfoPrompt = (product: CatalogItem, language: string): string => `
You are a creative product marketing expert. I need you to generate a catchy and compelling title and a super selling description for a product.

Product Details:
- Product Name: ${product.name}
- Product Sku: ${product.sku}
- Product Description: ${product.description}

Requirements:
- The title should be attention-grabbing and clearly convey what the product is.
- The description should highlight the product's strengths, unique aspects, and benefits.
- The title and description should be concise, engaging, and free of spelling and grammatical errors.
- The description must include any relevant keywords that can help improve search engine optimization.
- The description must include all the details provided in the product description.
- Note that you are cataloging an auto parts related product.
- The output must be in ${Language.getLanguageName(language)}.

Output JSON Format:
{
  "title": "Generated Title",
  "description": "Generated Description"
}
`;
