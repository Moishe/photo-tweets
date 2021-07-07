import React from 'react';
import Paper from '@material-ui/core/Paper';

const MAX_WIDTH = 50;
const MAX_HEIGHT = 50;

function calcScore(tweet) {
  var metrics = tweet.public_metrics;
  return (metrics.retweet_count + metrics.quote_count) * 5 + 
    metrics.like_count;
}

function multiplierForScore(score) {
  return Math.log(score);
}

function maxWidthForScore(score) {
  return Math.floor(MAX_WIDTH * multiplierForScore(score));
}

function maxHeightForScore(score) {
  return Math.floor(MAX_HEIGHT * multiplierForScore(score));
}

function calcWidth(photo, tweet) {
  var maxWidth = maxWidthForScore(calcScore(tweet))
  return Math.min(photo.width, maxWidth);
}

function calcHeight(photo, tweet) {
  var score = calcScore(tweet);
  var maxHeight = maxHeightForScore(score);
  var maxWidth = maxWidthForScore(score);
  if (photo.width <= maxWidth) {
    return Math.min(photo.height, maxHeight);    
  } else {
    return photo.height / (photo.width / maxWidth);
  }
}

function makeLink(user, tweet) {
  return "https://twitter.com/" + user.username + "/status/" + tweet.id;
}

export default class TweetPhoto extends React.Component {
  render() {
    return (
      <div className="tweet-photo">
        <a href={makeLink(this.props.user, this.props.tweet)}>
        <img 
          width={calcWidth(this.props.photo, this.props.tweet)} 
          height={calcHeight(this.props.photo, this.props.tweet)} 
          src={this.props.photo.url} 
          alt={this.props.tweet.text}>            
        </img>
        </a>
      </div>
    );
  }
}