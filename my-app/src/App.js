import React, { useState, useCallback, useEffect } from 'react'
import './App.css';

import Gallery from "react-photo-gallery";
import Carousel, { Modal, ModalGateway } from "react-images";
import TextField from '@material-ui/core/TextField';

export const useInput = initialValue => {
  const [value, setValue] = useState(initialValue);

  return {
    value,
    setValue,
    reset: () => setValue(""),
    bind: {
      value,
      onChange: event => {
        setValue(event.target.value);
      }
    }
  };
};

function App() {
  const [currentImage, setCurrentImage] = useState(0);
  const [viewerIsOpen, setViewerIsOpen] = useState(false);
  const [photos, setPhotos] = useState([]);

  const { value, bind, reset } = useInput('https://twitter.com/i/lists/1344411611960901637');

  const [currentUrl, setCurrentUrl] = useState('https://twitter.com/i/lists/1344411611960901637')

  async function getPhotos() {
    // let response = await fetch('http://127.0.0.1:5000/photos?url=' + encodeURI(value));
    let response = await fetch('/photos?url=' + encodeURI(value));
    response = await response.json();
    setCurrentUrl(value);
    setPhotos(response);
  }

  const reloadPhotos = (evt) => {
    evt.preventDefault();
    getPhotos();
  }

  useEffect(() => {
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
      <form onSubmit={reloadPhotos}>
        <TextField
            id="filled-full-width"
            helperText="Paste a Twitter URL to extract its photos"
            style={{ margin: 8 }}
            placeholder="https://twitter.com/i/lists/1344411611960901637"
            fullWidth
            margin="normal"
            InputLabelProps={{
              shrink: true,
            }}
            variant="outlined"
            {...bind}
          />
      </form>
      <p>currently viewing: {currentUrl}</p>
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
