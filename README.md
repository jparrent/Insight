# LettuceEats.me

Within this repo are the files for my Insight project, [LettuceEats](http://www.lettuceeats.me).

## Background

LettuceEats is a test web application designed to take the research out of going out to eat when you or someone in your party has either food allergies or food restrictions, e.g., tree nuts. Users can search by category, specify vegan, vegetarian, etc, or supply a string of other food items to avoid. LettuceEats then returns a curated list of recommended restaurants that are ranked by the number of acceptable menu items. 

For example, say you are either allergic to avocado, or simply wish to avoid it, in this case a search for 'avocado' would need to catch items such as guacamole, particularly when avocado is not mentioned in that menu. The motive behind LettuceEats is thus to enable free-text searching using Natural Language Processing (NLP).

## word2vec Model

To do this I relied on [word2vec](https://radimrehurek.com/gensim/models/word2vec.html) to produce a [word-embedding model](https://www.tensorflow.org/versions/r0.11/tutorials/word2vec/index.html). Using a [skip-gram](http://mccormickml.com/2016/04/19/word2vec-tutorial-the-skip-gram-model/) base model, I trained three distinct word models to act as the engine, the differences being the combination of [hierarchical softmax](http://sebastianruder.com/word-embeddings-softmax/index.html#hierarchicalsoftmax) and [negative sampling](http://sebastianruder.com/word-embeddings-softmax/index.html#negativesampling) used for each model. This was done
in order to reduce false-positives (e.g., matching on 'avocado' and 'cucumber'). 

## Training Data

With the help of the [Locu restaurant API](https://dev.locu.com), the model was trained on a collection of menus from cities across the US. Since the corpus was built from scratch, the validation of the model was checked by various test case 'by hand'. Overall the model's performance is thus far acceptable and could improve dramatically by adding recipe data.

### Disclaimers: 
The [Flask](http://flask.pocoo.org) web framework was hosted on an [AWS EC2 instance](https://aws.amazon.com/ec2/). Some of the restaurant data obtained from the Locu API is either out of date or incomplete, whereas only 25 restaurants have been collected per city. In a real world scenario, please inform your server if a person in your party has a food allergy before placing your order.
