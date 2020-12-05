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

const listData = [];
const majorWord = [];
fs.createReadStream('major_word.csv')
  .pipe(csv())
  .on('data', (row) => {
    majorWord.push(row);
  })
  .on('end', () => {
    console.log("Read major word");
  })

fs.createReadStream('frequency-2.csv')
  .pipe(csv())
  .on('data', (row) => {
    listData.push(row);
  })
  .on('end', async () => {
    const listVNWord = listData.filter(x => x.text.match(/[àảãáạăằẳẵắặâầẩẫấậđèẻẽéẹêềểễếệìỉĩíịòỏõóọôồổỗốộơờởỡớợùủũúụưừửữứựỳỷỹýỵ_]/g));
    const listShortVNWord = listVNWord.filter(x => !x.text.includes('_'));
    const listLongVNWord = listVNWord.filter(x => x.text.includes('_'));
    const otherData = _.difference(_.difference(listData, listShortVNWord), listLongVNWord);
    const notAlphabet = otherData.filter(x => x.text.match(/[^a-zA-Z\d\s:]/g));
    const onlyOneLetter = _.difference(otherData, notAlphabet).filter(x => x.text.length === 1);
    let otherWord = _.differenceBy(_.difference(_.difference(otherData, notAlphabet), onlyOneLetter), majorWord, 'text');
    let stopWordEng = await fs.readFileSync('en_stopword.txt', { encoding: 'utf-8' });
    stopWordEng = stopWordEng.split(/\r\n/g);
    const engStopWord = otherWord.filter(x => {
      return stopWordEng.findIndex(e => e === x.text) !== -1;
    });
    otherWord = _.difference(otherWord, engStopWord);


    writeCsv(listShortVNWord, 'short_vn_word.csv', header);
    writeCsv(listLongVNWord, 'long_vn_word.csv', header);
    writeCsv(otherWord, 'other_word.csv', header);
    writeCsv(notAlphabet, 'not_alphabet_word.csv', header);
    writeCsv(onlyOneLetter, 'only_one_letter.csv', header);
    writeCsv(engStopWord, 'en_stopword.csv', header);
  });
