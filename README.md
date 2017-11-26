# Ebleeni

Reads your face (and mind, of course), to foresee which programming language suits you the best.
Don't hesitate to be recognized! Event if you're not a programmer, ebleeni will poor oil on troubled water and offer smth. interesting for you!

Setup
-----

#### Local

Local setup:

    pip3 install -r requirements.txt

Run local web server:

    make run

Server will listen on `localhost:5000`.

#### Digitalocean

Build image:

    make build

Deploy image:

    DEPLOY_USER=myuser DEPLOY_HOST=myhost DEPLOY_PATH=/persistent/path DEPLOY_TMP_PATH=/persistent/path/tmp make deploy

#### App Engine

Build image:

    make ae-build

Deploy image:

    make ae-deploy

How is it operated
==================

To make it works you need follow this steps:
* Collect data for training
* Filter collected data
* Retrain TensorFlow ImageNet model
* Make it works on the web

#### Collecting data

Firs of all we had to decide on programming languages to use as our classes. To fulfill this task we download the list of whole programming languages used on GitHub and filter non-trendy ones.

To train the NN were looking for github avatars of users, written code on specific language. For each language we found the developer top-list and download whole the avatars from it.

#### Filter data

We used `OpenCV` to clear out avatars with no human face. Then we cropped each image with the face bounds offered by `OpenCV`.

#### Retrain model

We use Google Inception neural network as classifier. I must confess, we didn't create our own one from scratch and just retrained the last layer in Google model.

To some quality improvements we tested different hyperparameters like NN architecture, number of iterations and learning rate.

Use `Retrain.ipynb` notebook to train and test model.

#### Make it available on the web

GoogleAppEngine don't appreciate hube amount of work so we uploaded lightweight model to work on the web.
It is quantified version of NN with mobilenet v0.50 architecture works with 128x128 images.
