const csv = require('csv-parser');
const fs = require('fs');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const _ = require('lodash');

const writeCsv = (data, path, header) => {
  const csvWriter = createCsvWriter({
    path,
    header
  });
  csvWriter
    .writeRecords(data)
    .then(() => console.log('The CSV file was written successfully'));
}

const header = [
  { id: 'text', title: 'text' },
  { id: 'total', title: 'total' },
]

let listData = [];
const majorWord = [];
fs.createReadStream('other_word.csv')
  .pipe(csv())
  .on('data', (row) => {
    listData.push(row);
  })
  .on('end', () => {
    listData = listData.sort((a, b) => b.total - a.total);
    console.log(listData[0])

    writeCsv(listData, 'other_word.csv', header);
  })

