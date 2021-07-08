import React, { useState, useCallback, useEffect } from 'react'
import './App.css';

import Gallery from "react-photo-gallery";
import Carousel, { Modal, ModalGateway } from "react-images";
import TextField from '@material-ui/core/TextField';

// var photos = require('./photos.json');
// var simple_photos = require('./simple-photos.json')
/*
class App extends Component {
  state = {
    photos: []
  }

  componentDidMount() {
    fetch('http://127.0.0.1:5000/photos')
    .then(res => res.json())
    .then((data) => {
      this.setState({ photos: data })
    })
    .catch(console.log)
  }

  logit(foo) {
    console.log(foo);
    console.log(this);
  }
  
  render() {
      return (
        <div className="App">
          <form noValidate autoComplete="off">
            <TextField id="standard-basic" label="Standard" />
            <TextField id="filled-basic" label="Filled" variant="filled" />
            <TextField id="outlined-basic" label="Outlined" variant="outlined" />
          </form>
          <Gallery photos={this.state.photos} onClick={useCallback(logit, { photo, tweeturl })}/>
        </div>
    ) 
  }
}
*/
function App() {
  const [currentImage, setCurrentImage] = useState(0);
  const [viewerIsOpen, setViewerIsOpen] = useState(false);
  const [photos, setPhotos] = useState([]);

  useEffect(() => {
    async function getPhotos() {
      let response = await fetch('http://127.0.0.1:5000/photos');
      response = await response.json();
      setPhotos(response)
    }

    if (photos.length === 0) {
      getPhotos();
    }
  });

  const openLightbox = useCallback((event, { photo, index }) => {
    setCurrentImage(index);
    setViewerIsOpen(true);
  }, []);

  const closeLightbox = () => {
    setCurrentImage(0);
    setViewerIsOpen(false);
  };

  return (
    <div className="App">
      <TextField id="standard-basic" label="Standard" />
      <Gallery photos={photos} onClick={openLightbox} />
      <ModalGateway>
        {viewerIsOpen ? (
          <Modal onClose={closeLightbox}>
            <Carousel
              currentIndex={currentImage}
              views={photos.map(x => ({
                ...x,
                srcset: x.srcSet,
                caption: x.title
              }))}
            />
          </Modal>
        ) : null}
      </ModalGateway>
    </div>
  );
}

export default App;
