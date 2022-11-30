from keras.saving.save import load_model

import experiments_configuration.autoencoder_exp_config as autoencoder_config
from autoencoder import get_autoencoder_model
from keras_models.models import get_model
from utilities.data_utilities import get_transformed_data
from utilities.plot_utilities import plot_validation_and_train_loss, plot_validation_and_train_acc
from utilities.train_utilities import get_callbacks_for_training

autoencoder_saved_with_compress_path = f'{autoencoder_config.saved_models_path}autoencoder_with_compress.h5'

x_train, y_train, x_test, y_test = get_transformed_data(dataset_number_to_load=3)
output_classes = 7 # how many classes we have to classify
n_samples = x_train.shape[0]
n_inputs = x_train.shape[1] #aka number of features

# DEFINING AND TRAINING THE ENCODER
autoencoder_model = get_autoencoder_model(n_inputs, compress=False)
training_callbacks_autoencoder = get_callbacks_for_training(best_model_name="best_autoencoder_model")
# fit the autoencoder model to reconstruct input
history = autoencoder_model.fit(x_train, x_train,
                                epochs=autoencoder_config.n_epochs,
                                batch_size=16, verbose=2,
                                validation_data=(x_test, x_test),
                                callbacks=training_callbacks_autoencoder)
autoencoder_model.save(autoencoder_saved_with_compress_path)


# load the autoencoder model from file
encoder = load_model(autoencoder_saved_with_compress_path)
X_train_encode = encoder.predict(x_train)
X_test_encode = encoder.predict(x_test)

### ADDING AUTOENCODER TO EXISTING MODEL:
model_with_autoencoder = get_model(num_of_output_classes=output_classes, input_dim=40,  lr=autoencoder_config.learning_rate)

# fit the model on the training set
training_callbacks_model = get_callbacks_for_training(best_model_name="best_model_with_autoencoder")
model_with_autoencoder.fit(X_train_encode, y_train, callbacks=training_callbacks_model)

epoch_training_stopped_for_model_with_encoder = training_callbacks_model[0].stopped_epoch
if epoch_training_stopped_for_model_with_encoder==0:
    epoch_training_stopped_for_model_with_encoder = autoencoder_config.n_epochs

# make predictions on the test set and calculate classification accuracy
score, acc_test_with_autoencoder = model_with_autoencoder.evaluate(X_test_encode, y_test, batch_size=autoencoder_config.batch_size)
score_train, acc_train_with_autoencoder = model_with_autoencoder.evaluate(X_train_encode, y_train, batch_size=autoencoder_config.batch_size)
print('Test score with autoencoder :', score)
print('Test Accuracy with autoencoder:', acc_test_with_autoencoder)
print('Train Accuracy with autoencoder:', acc_train_with_autoencoder)

title_loss = f"Model loss with autoencoder,lr:{autoencoder_config.learning_rate},Samples:{n_samples}, Epochs:{epoch_training_stopped_for_model_with_encoder}, Test acc:{acc_test_with_autoencoder:.3f}, Train acc:{acc_train_with_autoencoder:.3f}"
title_acc = f"Model accuracy with autoencoder, Test acc:{acc_test_with_autoencoder:.3f}, Train acc:{acc_train_with_autoencoder:.3f}"

plot_validation_and_train_loss(autoencoder_config.loss_file_name_autoencoder,title_loss, history)
plot_validation_and_train_acc(autoencoder_config.accuracy_file_name_autoencoder,title_acc, history)
del model_with_autoencoder
del X_test_encode
del X_train_encode

# Without adding autoencoder in model
model_without_autoencoder = get_model(num_of_output_classes=output_classes, input_dim=40,  lr=autoencoder_config.learning_rate)
# fit the model on the training set
training_callbacks_model_without_autoencoder = get_callbacks_for_training(best_model_name="best_model_without_autoencoder")
model_without_autoencoder.fit(x_train, y_train, callbacks=training_callbacks_model_without_autoencoder)


epoch_training_stopped_for_model_without_autoencoder = training_callbacks_model_without_autoencoder[0].stopped_epoch
if epoch_training_stopped_for_model_without_autoencoder==0:
    epoch_training_stopped_for_model_without_autoencoder = autoencoder_config.n_epochs

# make predictions on the test set and calculate classification accuracy
score_without_autoencoder, acc_test_without_autoencoder = model_without_autoencoder.evaluate(x_test,
                                                                                             y_test,
                                                                                             batch_size=autoencoder_config.batch_size)
score_without_autoencoder_train, acc_train_without_autoencoder = model_without_autoencoder.evaluate(x_train,
                                                                                                    y_train,
                                                                                                    batch_size=autoencoder_config.batch_size)
print('Test score without autoencoder :', score_without_autoencoder)
print('Test Accuracy without autoencoder:', acc_test_without_autoencoder)
print('Train Accuracy without autoencoder:', acc_train_without_autoencoder)

title_loss_without_autoencoder = f"Model loss without autoencoder, lr:{autoencoder_config.learning_rate},Samples:{n_samples}, Epochs:{epoch_training_stopped_for_model_without_autoencoder}, Test acc:{acc_test_without_autoencoder:.3f}, Train acc:{acc_train_without_autoencoder:.3f}"
title_acc_without_autoencoder= f"Model accuracy without autoencoder, Test acc:{acc_test_without_autoencoder:.3f}, Train acc:{acc_train_without_autoencoder:.3f}"

plot_validation_and_train_loss(autoencoder_config.loss_file_name_without_autoencoder,title_loss_without_autoencoder, history)
plot_validation_and_train_acc(autoencoder_config.accuracy_file_name_without_autoencoder,title_acc_without_autoencoder, history)