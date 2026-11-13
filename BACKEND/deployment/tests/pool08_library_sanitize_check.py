"""Real image/video decoding in the three own sanitizers; never uses private user assets."""
import unittest,types,sys,importlib.util,io,tempfile,subprocess
from pathlib import Path
from PIL import Image,PngImagePlugin
ROOT=Path(__file__).resolve().parents[3]
def cases(folder,n):
 name='library_sanitize_'+str(n);pkg=types.ModuleType(name);pkg.__path__=[str(ROOT/folder)];sys.modules[name]=pkg
 def load(part):
  spec=importlib.util.spec_from_file_location(name+'.'+part,ROOT/folder/(part+'.py'));m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
 crm=load('crm');m=load('library_sanitize')
 class Checks(unittest.TestCase):
  def test_original_metadata_and_appendix_not_in_derivative(self):
   b=io.BytesIO();info=PngImagePlugin.PngInfo();info.add_text('private_marker','SECRET_TEST_ONLY');Image.new('RGB',(30,20)).save(b,format='PNG',pnginfo=info);raw=b.getvalue()+b'PRIVATE_APPENDIX';out,mime,meta=m.sanitize(raw,'image/png');self.assertNotIn(b'SECRET_TEST_ONLY',out);self.assertNotIn(b'PRIVATE_APPENDIX',out);self.assertEqual(mime,'image/png');self.assertEqual(meta['width'],30)
  def test_transparent_palette_logo_keeps_transparency(self):
   image=Image.new('P',(20,20));image.putpalette([0,0,0,255,255,255]+[0]*762);b=io.BytesIO();image.save(b,format='PNG',transparency=0);out,_,_=m.sanitize(b.getvalue(),'image/png');clean=Image.open(io.BytesIO(out));self.assertEqual(clean.mode,'RGBA');self.assertEqual(clean.getpixel((0,0))[3],0)
  def test_exif_orientation_is_baked_before_metadata_removal(self):
   image=Image.new('RGB',(40,20));exif=Image.Exif();exif[274]=6;b=io.BytesIO();image.save(b,format='JPEG',exif=exif);out,_,meta=m.sanitize(b.getvalue(),'image/jpeg');self.assertEqual((meta['width'],meta['height']),(20,40));self.assertEqual(len(Image.open(io.BytesIO(out)).getexif()),0)
  def test_wrong_format_animation_and_documents_rejected(self):
   for raw,mime in [(b'%PDF-private','application/pdf'),(b'<Invoice/>','image/png'),(b'<svg/>','image/svg+xml')]:
    with self.assertRaises(crm.CRMError):m.sanitize(raw,mime)
   b=io.BytesIO();Image.new('RGB',(10,10)).save(b,format='PNG')
   with self.assertRaises(crm.CRMError):m.sanitize(b.getvalue(),'image/jpeg')
  def test_reencodes_bounded_mp4_and_webm_without_metadata(self):
   with tempfile.TemporaryDirectory() as d:
    for ext,codec,mime in [('mp4','libx264','video/mp4'),('webm','libvpx-vp9','video/webm')]:
     p=Path(d)/('sample.'+ext);subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=64x48:r=10:d=1','-metadata','comment=PRIVATE_VIDEO_TEST','-c:v',codec,'-threads','1','-y',str(p)],check=True,capture_output=True);raw=p.read_bytes();clean,actual,meta=m.sanitize(raw,mime);self.assertEqual(actual,mime);self.assertNotIn(b'PRIVATE_VIDEO_TEST',clean);self.assertEqual((meta['width'],meta['height']),(64,48));self.assertGreater(meta['duration_seconds'],0);self.assertLess(len(clean),m.MAX_DELIVERY)
 Checks.__name__='OwnedSanitizer'+str(n);return Checks
for i,f in enumerate(['BACKEND/SGA-CD-BACKEND/app/commercial/pool08','BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/pool08','BACKEND/ANALEMATICA-BACKEND/gestion_comercial/pool08']):globals()['Owned'+str(i)]=cases(f,i)
if __name__=='__main__':unittest.main()
