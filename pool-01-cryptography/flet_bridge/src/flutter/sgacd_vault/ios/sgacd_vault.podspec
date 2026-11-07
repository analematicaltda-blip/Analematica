Pod::Spec.new do |s|
  s.name = 'sgacd_vault'
  s.version = '0.3.0'
  s.summary = 'Metadata-only native encrypted document vault for Flet.'
  s.homepage = 'https://github.com/analematicaltda-blip/SGA-CD'
  s.author = 'Analematica'
  s.license = { :type => 'Proprietary' }
  s.source = { :path => '.' }
  s.source_files = 'Classes/**/*.swift'
  s.dependency 'Flutter'
  s.platform = :ios, '15.0'
  s.swift_version = '5.0'
  s.pod_target_xcconfig = { 'DEFINES_MODULE' => 'YES' }
end
