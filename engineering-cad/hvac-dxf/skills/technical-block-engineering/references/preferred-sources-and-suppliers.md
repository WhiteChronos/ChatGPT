# Preferred Sources and Real-Supplier Policy

Use the manufacturer as the primary technical authority and the manufacturer's own partner/distributor system as the only authority for deciding whether a supplier is genuine/authorized for that brand.

## Seed brand registry

### WEG
- Manufacturer authority: `weg.net`
- Authorized-channel verification: WEG `Where to Buy`
- Brazil locator: `https://www.weg.net/institutional/BR/pt/contact/where-to-buy`
- Rule: a WEG seller not verifiable through WEG's own channel is not an authorized-source reference.

### Schneider Electric
- Manufacturer authority: `se.com`
- Brazil partner locator: `https://www.se.com/br/pt/work/support/locator/map/`
- Brazil distributors: `https://www.se.com/br/pt/partners/distributors/`
- Rule: use Schneider's own partner/distributor listings to validate channel status.

### Phoenix Contact
- Manufacturer authority: `phoenixcontact.com`
- Brazil partners/distributors page: `https://www.phoenixcontact.com/pt-br/empresa/parceiros-distribuidores-fornecedores`
- Rule: distributors must be reachable from or listed by Phoenix Contact's official channel.

### Rockwell Automation / Allen-Bradley
- Manufacturer authority: `rockwellautomation.com`
- Authorized channel: Rockwell Automation PartnerNetwork / Sales & Partners
- Rule: Rockwell explicitly warns that authentic Allen-Bradley / Rockwell products should be purchased from authorized sources; validate against PartnerNetwork.

### Daikin
- Manufacturer authority: `daikin.com.br` / official Daikin regional site
- Brazil distributor locator: `https://www.daikin.com.br/onde-comprar/distribuidor`
- Rule: use Daikin's own distributor/credenciado network for supplier validation.

### Belimo
- Manufacturer authority: `belimo.com`
- Brazil distributor lookup: `https://www.belimo.com/br/en_US/contact/channels/distributor-lookup`
- Rule: supplier status must match Belimo's own distributor classification.

### Vaisala
- Manufacturer authority: `vaisala.com`
- Brazil partner finder: `https://www.vaisala.com/en/partners/find-partner?field_countries_value=BR`
- Rule: use the partner finder to distinguish distributors from service partners.

## Brands not yet registered

For any other brand:
1. identify the official manufacturer domain;
2. find the official distributor/partner locator or official partner page;
3. validate the supplier from that brand-owned source;
4. add the brand to `brand-authority-registry.yaml`;
5. until step 3 succeeds, use manufacturer-direct technical sources only.

## CAD aggregators

Platforms such as 3Dfindit/TraceParts may be used to locate CAD, but they do not by themselves establish the commercial authorization of a seller. For final CAD geometry, preserve the manufacturer/model/file provenance and cross-check against the official manufacturer identity.
