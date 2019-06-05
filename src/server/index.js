const express = require('express');
const bodyParser = require('body-parser');
var fileUpload = require('express-fileupload');
const app = express();
const port = process.env.PORT || 5000;
const Sequelize = require('sequelize');
const tmp = require('tmp');
const { check, param, validationResult } = require('express-validator/check');
const { exec } = require('child_process');
const uuidv1 = require('uuid/v1');
const fs = require('fs');
const ReportTemplate = require('./ReportTemplate');
const pdf = require('html-pdf');

const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: 'database.sqlite'
});

const Model = Sequelize.Model;

class Test extends Model {}

Test.init({
  // attributes
  id: {
    type: Sequelize.STRING,
    primaryKey: true,
    allowNull: false
  },
  email: {
    type: Sequelize.STRING,
    allowNull: false
  },
  droneID: {
    type: Sequelize.STRING,
    allowNull: false
  },
  bundle: {
    type: Sequelize.BLOB,
    allowNull: false
  },
  truth: {
    type: Sequelize.BLOB,
    allowNull: false
  },
  report: {
    type: Sequelize.BLOB,
    allowNull: true
  },
  verified: {
    type: Sequelize.BOOLEAN,
    allowNull: false
  },
  // Timestamps
  createdAt: Sequelize.DATE,
  updatedAt: Sequelize.DATE
}, {
  sequelize,
  modelName: 'test'
  // options
});

sequelize.sync();

app.use(express.static('public'))
app.use(express.static('dist'))
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(fileUpload({
	limits: { 
		fileSize: 64 * 1024 * 1024,
		fields: 50,
		files: 1,
    parts: 51
  },
    useTempFiles : true,
    tempFileDir : '/tmp/'
}));

app.post('/api/generate', [check('formEmail').isEmail(), check('formDroneID').exists({"checkNull": true, "checkFalsy": true})], (req, res) => {
  let tmpdir = tmp.dirSync();
  let email = req.body.formEmail;
  let droneId = req.body.formDroneID;
  let area = req.body.formTestArea;
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    res.status(422).json({ success: false, msg: "validation errors" });
    return;
  }
  if(!req.files.formDronePublicKey) {
    res.status(422).json({ success: false, msg: "please select public key" });
    return;
  }
  let droneKeyFile = req.files.formDronePublicKey.tempFilePath;
  exec(`python3 ./generate_bundle.py --id ${droneId} --key ${droneKeyFile} --area '${area}' --bundle ${tmpdir.name}/bundle.zip --truth ${tmpdir.name}/truth.bin`, (err, stdout, stderr) => {
    if (err) {
      console.log(err);
      tmpdir.removeCallback();
      res.status(500).json({ success: false, msg: "exec error" });
      return;
    }
    Test.create({
      id: uuidv1(),
      droneID: droneId,
      email: email,
      bundle: fs.readFileSync(`${tmpdir.name}/bundle.zip`),
      truth: fs.readFileSync(`${tmpdir.name}/truth.bin`),
      report: null,
      verified: false
    })
    .then(test => {
      res.json({"success": true, "testId": test.id});
    });
    tmpdir.removeCallback();
  });
});

app.get('/api/bundle/:id', [param('id').exists({"checkNull": true, "checkFalsy": true})], (req, res) => {
  Test.findOne({
    where: {
      id: req.params.id,
      verified: false
    }
  }).then(test => {
    if(test) {
      res.writeHead(200, {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename=' + req.params.id + '.zip',
        'Content-Length': test.bundle.length
      });
      res.end(test.bundle);
    } else {
      res.status(404).json({ success: false, msg: "test verified or not found"});
    }
  });  
});

app.get('/api/report/:id', [param('id').exists({"checkNull": true, "checkFalsy": true})], (req, res) => {
  Test.findOne({
    where: {
      id: req.params.id,
      verified: true
    }
  }).then(test => {
    if(test) {
      res.writeHead(200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename=' + req.params.id + '.pdf',
        'Content-Length': test.report.length
      });
      res.end(test.report);
    } else {
      res.status(404).json({ success: false, msg: "test not verified or not found" });
    }
  });  
});

app.post('/api/verify', [check('formEmail').isEmail(),
  check('formTestID').exists({"checkNull": true, "checkFalsy": true}),
  check('s1').exists({"checkNull": true, "checkFalsy": true}),
  check('s2').exists({"checkNull": true, "checkFalsy": true}),
  check('s3').exists({"checkNull": true, "checkFalsy": true}),
  check('s4').exists({"checkNull": true, "checkFalsy": true}),
  check('s5').exists({"checkNull": true, "checkFalsy": true})], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    res.status(422).json({ success: false, "msg": "validation errors" });
    return;
  }
  if(!req.files.s6) {
    res.status(422).json({ success: false, "msg": "please select breach log" });
    return;
  }
  Test.findOne({
    where: {
      id: req.body.formTestID,
      verified: false
    }
  }).then(test => {
    if(test) {
      if(req.body.formEmail !== test.email) {
        res.status(422).json({ success: false, msg: "email do not match"});
        return;
      }
      let tmpdir = tmp.dirSync();
      fs.writeFileSync(`${tmpdir.name}/truth.bin`, test.truth);
      let breachLogFile = req.files.s6.tempFilePath;
      exec(`python3 ./verify_results.py --truth ${tmpdir.name}/truth.bin --s1 ${req.body.s1} --s2 ${req.body.s2} --s3 ${req.body.s3} --s4 ${req.body.s4} --s5 ${req.body.s5} --breach_log ${breachLogFile} --report ${tmpdir.name}/report.json`, (err, stdout, stderr) => {
        if (err) {
          console.log(err);
          tmpdir.removeCallback();
          res.status(500).json({ success: false, msg: "exec error" });
          return;
        }
        let report = JSON.parse(fs.readFileSync(`${tmpdir.name}/report.json`));
        let test_result = [];
        let passed = [];
        report.forEach(element => {
          test_result.push(element.test);
          if(element.passed) {
            passed.push("PASSED");
          } else {
            passed.push("FAILED");
          }
        });
        let template = ReportTemplate({"testId": test.id, "droneId": test.droneID, "email": test.email, "test": test_result, "result": passed });
        pdf.create(template, {}).toBuffer((err, buf) => {
          Test.update({ report: buf, "verified": true }, {
            where: {
              id: req.body.formTestID
            }
          }).then(test => {
            res.json({"success": true, "testId": test.id});
          });
        });
        tmpdir.removeCallback();
      });
    } else {
      res.status(422).json({ success: false, msg: "test not found"});
      return;
    }
  });  
});

app.listen(port, "127.0.01", () => console.log(`Listening on port ${port}`));