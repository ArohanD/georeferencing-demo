"""Recreate the manually inspected, pre-fit point selection. No network access."""
import csv, json, hashlib, zipfile, io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'data/points'; P.mkdir(exist_ok=True)
z=zipfile.ZipFile(ROOT/'data/reference/PopulatedPlaces_National_Text.zip')
rows=list(csv.DictReader(io.StringIO(z.read('Text/PopulatedPlaces_National.txt').decode('utf-8-sig')),delimiter='|'))
ref={r['feature_id']:r for r in rows}
# Pixel selections made on the original-resolution image and visually checked
# in outputs/point-inspection.jpg BEFORE evaluating any transformation.
items=[
 ('Salisbury',4012,3463,'994186','fit','Original town square/grid; approximate symbol center.'),
 ('Hillsborough',6438,2538,'986830','fit','Town grid north of Eno River; approximate grid center.'),
 ('Bethania',4288,2310,'1006108','fit','Bethania symbol, distinct from adjacent Bethabara and Salem.'),
 ('Halifax',9138,2170,'986304','fit','Town symbol on south/west side of Roanoke River.'),
 ('Edenton',10905,2580,'1025302','fit','Town grid on Albemarle Sound; not the label text.'),
 ('New Bern',10082,4694,'1013911','fit','Town grid at Trent/Neuse junction; NOT the Gov House label.'),
 ('Beaufort',10564,6025,'1019024','fit','Mainland town symbol; no inlet/shoreline point used.'),
 ('Wilmington',8313,7348,'1023269','fit','Town symbol on east side of Cape Fear below branch junction.'),
 ('Salem',4470,2500,'1022467','check','Forsyth County Salem; not another same-name town or Winston-Salem centroid.'),
 ('Tarboro',9123,3209,'1022886','check','Tarrburg symbol beside Tar River bend.'),
 ('Hertford',11136,2220,'1025382','check','Hartpford symbol at Perquimans River; spelling variant.'),
 ('Bath',10710,4012,'1018985','check','Town symbol at Bath Creek; not modern shoreline vertex.'),
 ('Nixonton',11589,2230,'1025582','excluded','Identifiable symbol, but colonial-core continuity not researched; northeast cluster already represented.'),
 ('Brunswick Town',8094,7810,'','excluded','Ruins potentially strong; modern Brunswick in Columbus County is a DIFFERENT place. Need archaeological town footprint coordinate.'),
 ('Cross Creek',6784,4829,'','excluded','Cross Creek and Campbellton were distinct; modern Fayetteville point not accepted.'),
 ('Haw–Deep river junction',None,None,'','excluded','Potential natural anchor; exact channel junction and historical persistence not established. No coordinate guessed.'),
]
fields=['point_id','feature_name','pixel_x','pixel_y','longitude','latitude','reference_crs','gnis_id','reference_source','matching_rationale','confidence','ambiguity','role']
out=[]
for i,(name,x,y,gid,role,why) in enumerate(items,1):
 r=ref.get(gid,{})
 out.append(dict(zip(fields,[f'P{i:02}',name,x,y,r.get('prim_long_dec',''),r.get('prim_lat_dec',''),'EPSG:4269' if gid else '',gid,'https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/Topical/PopulatedPlaces_National_Text.zip' if gid else '',why,'medium identity; low-to-medium positional' if gid else 'unresolved','GNIS place proxy and generalized town symbol may differ by hundreds of metres or kilometres; no exact colonial landmark established.' if gid else why,role])))
def save(name,rr):
 with (P/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rr)
save('candidates.csv',out)
save('fitting.csv',[r for r in out if r['role']=='fit'])
save('checks.csv',[r for r in out if r['role']=='check'])
reviewfields=fields+['decision_accept_reject_revise','corrected_pixel_x','corrected_pixel_y','corrected_longitude','corrected_latitude','corrected_crs','correction_source','reviewer_notes']
if not (P/'review.csv').exists():
 with (P/'review.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=reviewfields);w.writeheader();w.writerows(out)
lock={'status':'provisional town-proxy experiment','selection':'8 fitting and 4 checks fixed before first fit; no tuning against checks','pixel_convention':'Continuous image coordinates; upper-left outer corner=(0,0); x right, y down; pixel centers at n+0.5. Coordinates rounded to integer pixel-edge units, manual precision ~10–30 pixels, town symbol extent often larger. Source 13949 x 9524.','source_image':'collet-1770-loc-copy1.jp2','fit_sha256':hashlib.sha256((P/'fitting.csv').read_bytes()).hexdigest(),'checks_sha256':hashlib.sha256((P/'checks.csv').read_bytes()).hexdigest(),'inspection':'Whole image and enlarged crops inspected, followed by original-resolution 500 x 500 crops with crosshairs. Enlarged regional views used crop offset + displayed coordinate * original_crop_dimension/display_dimension. Final positions checked against original pixel coordinates in annotated crops.'}
(P/'selection.json').write_text(json.dumps(lock,indent=2)+'\n')
print('Saved 16 candidates: 8 fitting, 4 checking, 4 excluded. Review CSV preserved if present.')
