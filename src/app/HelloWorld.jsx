import React from 'react';
import { Button, Tabs, Tab, Form, Container, Row, Col, Modal, Alert } from 'react-bootstrap';
//import Container from 'react-bootstrap/Container'

class GenerateTestCases extends React.Component {

    constructor(props, context) {
      super(props, context);
      this.handleSubmit = this.handleSubmit.bind(this);
      this.handleShow = this.handleShow.bind(this);
      this.handleClose = this.handleClose.bind(this);
      this.state = {
        "popup": false,
        "showAlert": false,
        "alertText": ""
      }
    }

    handleClose() {
      this.setState({ show: false });
    }
  
    handleShow() {
      this.setState({ show: true });
    }

    handleSubmit(event) {
      event.preventDefault();
      const data = new FormData(event.target);
      console.log(data);
      
      fetch('/api/generate', {
        method: 'POST',
        body: data,
      })
      .then(response => response.json())
      .then((response) => {
        if(response.success) {
          this.setState({
            "showAlert": false,
            testID: response.testId
          });
          this.handleShow();
        } else {
          this.setState({
            showAlert: true,
            alertText: response.msg?response.msg:"unknown error"
          });
        }
        console.log(response);
      });
    }

    render() {
        return (
          <>
          <Form onSubmit={this.handleSubmit}>
            <Form.Group controlId="formEmail">
                <Form.Label>Email address</Form.Label>
                <Form.Control name="formEmail" type="email" placeholder="Enter email" required/>
            </Form.Group>
            <Form.Group controlId="formDroneID">
              <Form.Label>Drone ID</Form.Label>
              <Form.Control name="formDroneID" type="text" placeholder="Enter Drone ID" required/>
            </Form.Group>
            <Form.Group controlId="formPublicKey">
              <Form.Label>Public Key</Form.Label>
              <Form.Control name="formDronePublicKey" type="file" placeholder="Enter Drone Key" required/>
              <Form.Text className="text-muted">
                Drone key in PEM format.
              </Form.Text>
            </Form.Group>
            <Form.Group controlId="testArea">
              <Form.Label>Test Area</Form.Label>
              <Form.Control name="formTestArea" as="textarea" rows="3" placeholder="Test Area" required>
              [[77.609316, 12.934158], [77.609852, 12.934796],[77.610646, 12.934183], [77.610100, 12.933551], [77.609316,12.934158]]
              </Form.Control>
            </Form.Group>
            <Alert show={this.state.showAlert} variant="warning">
              <Alert.Heading>Something went wrong</Alert.Heading>
              <p>
                {this.state.alertText}
              </p>
            </Alert>
            <Button variant="primary" className="float-right" type="submit">
              Generate
            </Button>
          </Form>
          <Modal show={this.state.show} onHide={this.handleClose}>
            <Modal.Header closeButton>
              <Modal.Title>Test Generated</Modal.Title>
            </Modal.Header>
            <Modal.Body>Test ID: {this.state.testID}</Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={this.handleClose}>
                Close
              </Button>
              <Button target="_blank" variant="primary" onClick={this.handleClose} href={`/api/bundle/${this.state.testID}`}>
                Download
              </Button>
            </Modal.Footer>
          </Modal>
          </>);
    }

}

class VerifyTestCases extends React.Component {

    constructor(props, context) {
      super(props, context);
      this.handleSubmit = this.handleSubmit.bind(this);
      this.handleShow = this.handleShow.bind(this);
      this.handleClose = this.handleClose.bind(this);
      this.state = {
        "popup": false,
        "showAlert": false,
        "alertText": ""
      }
    }

    handleClose() {
      this.setState({ show: false });
    }
  
    handleShow() {
      this.setState({ show: true });
    }

    handleSubmit(event) {
      event.preventDefault();
      const data = new FormData(event.target);
      let testId = data.get("formTestID");
      if(!data.has("s1")) data.set("s1", "0")
      if(!data.has("s2")) data.set("s2", "0")
      if(!data.has("s3")) data.set("s3", "0")
      if(!data.has("s4")) data.set("s4", "0")
      
      fetch('/api/verify', {
        method: 'POST',
        body: data,
      })
      .then(response => response.json())
      .then((response) => {
        if(response.success) {
          this.setState({
            "showAlert": false,
            testID: testId
          });
          this.handleShow();
        } else {
          this.setState({
            showAlert: true,
            alertText: response.msg?response.msg:"unknown error"
          });
        }
        console.log(response);
      });
    }

    render() {
        return (
        <>
          <Form onSubmit={this.handleSubmit}>
            <Form.Group as={Row} controlId="formEmail">
                <Form.Label column sm={2}>Email address</Form.Label>
                <Col sm={10}>
                <Form.Control name="formEmail" type="email" placeholder="Enter email"  required/>
                </Col>
            </Form.Group>
            <Form.Group as={Row} controlId="formTestID">
                <Form.Label column sm={2}>Test ID</Form.Label>
                <Col sm={10}>
                <Form.Control name="formTestID" type="text" placeholder="Enter Test ID"  required/>
                </Col>
            </Form.Group>
            <Form.Group as={Row} controlId="s1">
              <Form.Label column sm={2}>Testcase 1</Form.Label>
              <Col sm={10}>
              <Form.Check value="1" name="s1" label="Armed with permission_artifact_1.xml" />
              </Col>
            </Form.Group>
            <Form.Group as={Row} controlId="s2">
              <Form.Label column sm={2}>Testcase 2</Form.Label>
              <Col sm={10}>
              <Form.Check value="1" name="s2" label="Armed with permission_artifact_2.xml" />
              </Col>
            </Form.Group>
            <Form.Group as={Row} controlId="s3">
              <Form.Label column sm={2}>Testcase 3</Form.Label>
              <Col sm={10}>
              <Form.Check value="1" name="s3" label="Armed with permission_artifact_3.xml" />
              </Col>
            </Form.Group>
            <Form.Group as={Row} controlId="s4">
              <Form.Label column sm={2}>Testcase 4</Form.Label>
              <Col sm={10}>
              <Form.Check value="1" name="s4" label="Armed with permission_artifact_4.xml" />
              </Col>
            </Form.Group>           
            <Form.Group as={Row} controlId="s5">
              <Form.Label column sm={2}>Testcase 5</Form.Label>
              <Col sm={10}>
              <Form.Control name="s5" type="file" placeholder="Log generated with permission_artifact_breach"  required/>
              <Form.Text className="text-muted">
              Log generated with permission_artifact_breach.xml
              </Form.Text>
              </Col>
            </Form.Group>
            <Alert show={this.state.showAlert} variant="warning">
              <Alert.Heading>Something went wrong</Alert.Heading>
              <p>
                {this.state.alertText}
              </p>
            </Alert>
            <Button variant="primary" className="float-right" type="submit">
              Verify
            </Button>
          </Form>
          <Modal show={this.state.show} onHide={this.handleClose}>
            <Modal.Header closeButton>
              <Modal.Title>Download Report</Modal.Title>
            </Modal.Header>
            <Modal.Body>Test ID: {this.state.testID}</Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={this.handleClose}>
                Close
              </Button>
              <Button target="_blank" variant="primary" onClick={this.handleClose} href={`/api/report/${this.state.testID}`}>
                Download
              </Button>
            </Modal.Footer>
          </Modal>
          </>);
    }

}

class DownloadTest extends React.Component {

  constructor() {
    super();
    this.state = {
      "id": ""
    };
    this.handleChange=this.handleChange.bind(this);
  }
  
  handleChange(e){
    this.setState({"id": e.target.value});
  }

  render() {
      return (<Form onSubmit={this.handleSubmit}>
          <Form.Group as={Row} controlId="formTestID">
              <Form.Label column sm={2}>Test ID</Form.Label>
              <Col sm={10}>
              <Form.Control name="formTestID" onChange={this.handleChange} type="text" value={this.state.id} placeholder="Enter Test ID"  required/>
              </Col>
          </Form.Group>
          <Button target="_blank" variant="primary" className="float-right" href={`/api/bundle/${this.state.id}`}>
            Download
          </Button>
        </Form>);
  }

}

class DownloadReport extends React.Component {

  constructor() {
    super();
    this.state = {
      "id": ""
    };
    this.handleChange=this.handleChange.bind(this);
  }
  
  handleChange(e){
    this.setState({"id": e.target.value});
  }

  render() {
      return (<Form onSubmit={this.handleSubmit}>
          <Form.Group as={Row} controlId="formTestID">
              <Form.Label column sm={2}>Test ID</Form.Label>
              <Col sm={10}>
              <Form.Control name="formTestID" onChange={this.handleChange} type="text" value={this.state.id} placeholder="Enter Test ID"  required/>
              </Col>
          </Form.Group>
          <Button target="_blank" variant="primary" className="float-right" href={`/api/report/${this.state.id}`}>
            Download
          </Button>
        </Form>);
  }

}

class HelloWorld extends React.Component {
    render() {
    	return (
          <div>&nbsp;
          <Tabs defaultActiveKey="generate" id="uncontrolled-tab-example" >
            <Tab eventKey="generate" title="Generate Test" style={{"padding": 24}}>
                <GenerateTestCases />
            </Tab>
            <Tab eventKey="verify" title="Verify Test" style={{"padding": 24}}>
              <VerifyTestCases />
            </Tab>
            <Tab eventKey="test" title="Download Test" style={{"padding": 24}}>
              <DownloadTest />
            </Tab>
            <Tab eventKey="download" title="Download Report" style={{"padding": 24}}>
              <DownloadReport />
            </Tab>
          </Tabs>
          </div>
        );
    }
}
export default HelloWorld;