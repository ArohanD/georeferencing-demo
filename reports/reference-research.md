# Reference evidence and unresolved matching questions

Research date: 2026-09-17. This note establishes candidate identities, not pixel matches or surveyed coordinates. No coordinates have been inferred from town names. Historic symbols must be inspected in the original scan and matched to a documented place, not to label text.

## Coordinate conventions

The saved Library of Congress catalog record (`data/metadata/loc-item.json`, [item 83693769](https://www.loc.gov/item/83693769/)) confirms publication by S. Hooper on May 1, 1770, and notes two copies whose coloration differs. Its notes do **not** establish a prime meridian or modern datum. Searches did not establish a documented Collet-to-WGS84 longitude conversion. Direct inspection of the border inscriptions is necessary. Even a printed London or Greenwich meridian would not establish modern geodetic equivalence or correct historical survey errors. Do not fit modern coordinates to printed graticules by assumption.

The [LOC Mouzon catalog](https://www.loc.gov/resource/g3900.ar139404/) explicitly describes that different map's prime meridian as London. This is not evidence for Collet's convention. [NCpedia's Collet biography](https://www.ncpedia.org/biography/collet-collett-john) describes Collet as a source for Mouzon's northern portion, so these maps would also be correlated evidence rather than independent validation.

## Historic-site candidates

| Candidate | Evidence and appropriate matching use | Unresolved issue |
|---|---|---|
| Brunswick Town | [NC Historic Sites history](https://historicsites.nc.gov/all-sites/brunswick-town-and-fort-anderson/history) identifies the abandoned colonial town, archaeological foundations, and surviving walls of St. Philip's Church dating from 1754. Strong historic-place evidence. | Use the town ruin footprint or an identifiable church symbol, not modern Brunswick or the highway marker (which is displaced from the site). |
| Bath | [NC Historic Sites](https://historicsites.nc.gov/all-sites/historic-bath/history) documents the colonial town and Palmer-Marsh House. The [NPS nomination](https://npgallery.nps.gov/GetAsset/477920ab-1d57-4f1a-96d1-b02a15bb8654/) supplies a boundary description at Main/Carteret and historic coordinate text. | Nomination datum is not established here; the house is not automatically the point represented by a town symbol. |
| Edenton | [State site](https://historicsites.nc.gov/all-sites/historic-edenton) identifies the 1767 courthouse. [Nomination CO0003](https://files.nc.gov/ncdcr/nr/CO0003.pdf) identifies the courthouse green and its earlier courthouse use. | Match the town grid/green only if image detail supports it; current visitor center is not a historic anchor. |
| Halifax | [DNCR town history](https://www.dncr.nc.gov/blog/2016/11/21/creating-town-halifax) describes the 1757 grid and original lots preserved in the historic site. [NC Archaeology](https://archaeology.ncdcr.gov/blog/historyinsites/historichalifaxcourthouse) references Sauthier's 1769 town plan and archaeological work. | Town-scale symbol may not resolve courthouse location; later town expansion must be excluded. |
| Hillsborough | [Orange County Historical Museum](https://www.orangehistorync.org/our-building) identifies N. Churton/W. Tryon as lot 98 in Churton's 1754 survey, with a church built after 1768. | Supports colonial core, not identification of a particular Collet symbol. |
| Salisbury | [City history](https://salisburync.gov/Visitors) documents Rowan Court House in 1753, Salisbury in 1755, and the original central square/grid. | The town symbol represents an area. A modern municipal centroid is not a colonial courthouse match. |
| New Bern | [Tryon Palace history](https://www.tryonpalace.org/the-palace-historic-homes/tryon-palace/palace-history) documents 1767–1770 construction and reconstruction on excavated original foundations. | Reconstructed building is spatially useful only if the map depicts it; town symbol and Trent/Neuse junction are different possible anchors. |
| Beaufort | [Municipal colonial history](https://www.beaufortnc.org/media/3471) documents the October 1713 town survey from land/deed evidence. | Use historic mainland town grid, not today's inlet geometry. |
| Cross Creek / Campbellton | [Cumberland County library history](https://www.co.cumberland.nc.us/departments/library-group/library/america-250-nc/cumberland-county-history) discusses separate communities. [NC SHPO-hosted 2018 study](https://files.nc.gov/ncdcr/historic-preservation-office/PDFs/ER%2014-1475_Addendum7.pdf) describes their separate origins and later merger. | They were distinct in 1770. Assigning both to a modern Fayetteville center would be erroneous; investigate each actual symbol separately. |
| Wilmington | Candidate identity plausible but no feature-specific colonial anchor was established in this bounded research pass. | Require a documented colonial street intersection/core or distinguishable confluence before accepting. |

## Modern reference data

[USGS GNIS](https://www.usgs.gov/national-hydrography/hydrography-and-geographic-names) is an official feature-name source, but names alone do not establish historical spatial continuity. [USGS Circular 1011](https://pubs.usgs.gov/circ/1011/report.pdf) defines primary coordinates as approximate centers of area features and mouths of linear features. Consequently a populated-place point is a regional town proxy, not a surveyed 1770 settlement center; a stream primary point can help identify its mouth but still needs visual and historical examination. Record the actual reference dataset, feature identifier, datum and extraction date in any accepted GCP row.

[NC HPOWEB 2.0](https://www.arcgis.com/home/item.html?id=d2d04d8d7e03403f889419526e682529) provides historic resource locations and district boundaries. The service description explicitly excludes archaeological data. Historic district geometry and nomination maps are useful corroboration, not automatic town-center coordinates. Public topographic hydrography can corroborate river junctions; migrating shorelines and inlets require separate historical justification.

## Source leads and existing overlays

[NCpedia's map excerpt](https://www.ncpedia.org/media/map/compleat-map-north-carolina-1770) identifies the 1770 Collet map, explicitly calls its displayed image an excerpt, labels it public domain, and links UNC legacy record `ncmaps/467`. That establishes a real UNC lead; it does not verify either supplied UUID. Both [UNC lead 1](https://dcr.lib.unc.edu/record/cb7ee34b-566c-4f4b-881a-4692f3484a0b) and [UNC lead 2](https://dcr.lib.unc.edu/record/4852994f-b7aa-4222-9cc1-82aeca2f4b47) failed to open through the browsing tool, and exact-ID search yielded no identity evidence. Record them as unresolved, not Collet.

The three saved ArcGIS item JSON files were inspected:

- [Mouzon item](https://www.arcgis.com/home/item.html?id=6750d9a5986d4490b75ea14507a94ec8): `mouzonimage`, owner `dloberger`, Map Service, description only says georeferenced Mouzon image; no license or attribution field. No GCPs or accuracy evidence established.
- [Moseley item](https://www.arcgis.com/home/item.html?id=2f225e9c638c45adb8899d33d5c9d0b6): explicitly 1733 and clipped to a project area. Cites [ECU 51135](https://digital.lib.ecu.edu/51135); research/teaching/private-study reuse wording. Not Collet.
- [Cowley/Moseley item](https://www.arcgis.com/home/item.html?id=37cff25f29d84d57913e6eeb72743991): explicitly 1737, georeferencing attributed to Wake Forest CHARG. Describes a color copy of a manuscript in private ownership, presented by NC State Archives for research/education; commercial use requires prior permission. Not an original Collet scan.

Item identity and descriptive metadata were verified; service tile accuracy, transformations, and GCPs were not. None should serve as independent ground truth for the Collet pilot.
