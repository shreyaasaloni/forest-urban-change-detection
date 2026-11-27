// West Hyderabad: [west, south, east, north]
var area = ee.Geometry.Rectangle([78.22, 17.34, 78.42, 17.50]);
var BANDS = ['B2', 'B3', 'B4', 'B8', 'B11'];

function prepare(img) {
  var scl = img.select('SCL');
  var bad = scl.eq(1).or(scl.eq(3)).or(scl.eq(8))
              .or(scl.eq(9)).or(scl.eq(10)).or(scl.eq(11));
  return img.addBands(img.select('B11').resample('bilinear'), null, true)
            .updateMask(bad.not());
}

[2020, 2025].forEach(function (year) {
  // Post-monsoon: forests are still green and clouds are usually low
  var collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(area)
    .filterDate(year + '-10-15', year + '-12-15')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

  print('Images found in ' + year, collection.size());

  var image = collection.map(prepare)
    .median()
    .select(BANDS)
    .clip(area)
    .unmask(0)
    .round()
    .toUint16();

  Map.addLayer(image, {bands: ['B4', 'B3', 'B2'], min: 0, max: 3000}, 'RGB ' + year);

  Export.image.toDrive({
    image: image,
    description: 's2_' + year,
    fileNamePrefix: 's2_' + year,
    folder: 'satellite_data',
    region: area,
    scale: 10,
    crs: 'EPSG:32644',
    maxPixels: 1e9
  });
});

Map.centerObject(area, 12);