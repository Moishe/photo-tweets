import logo from './logo.svg';
import './App.css';
import TweetPhoto from './TweetPhoto.js'
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import { makeStyles } from '@material-ui/core/styles';

var photos = require('./photos.json');

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
}));

function App() {
  const classes = useStyles();

  return (
    <div className="App">
      <Grid container spacing={3}>
      {photos.map(photo => (
      <Grid item xs>
        <Paper className={classes.paper}>
          <TweetPhoto photo={photo.photo} user={photo.user} tweet={photo.tweet}></TweetPhoto>
        </Paper>
      </Grid>
      ))}
      </Grid>
    </div>
  );
}

export default App;
