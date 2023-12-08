"""
    Define generator for GAN model
"""
import tensorflow as tf
import tensorflow.keras as keras


class Generator():
    def __init__(self, latent_dim, caption_dim, vocab_size, embed_dim, n_nodes=(128 * 53 * 53)):
        """
            Define the generator model
            Inputs:
                latent_dim: dimension of the latent space
                caption_dim: dimension of the caption
                vocab_size: size of the vocabulary
                embed_dim: dimension of the embedding
                n_nodes: number of nodes in the dense layer
            Output:
                model: the generator model
        """
        self.latent_dim = latent_dim
        self.caption_dim = caption_dim
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.n_nodes = n_nodes
        self.model = self.caption_enhanced_generator()
        self.model_summmary = self.model.summary()
        self.model_layout = self.plot_model()


    def caption_enhanced_generator(self):
        """
            Define the generator model
        """

        # vectorized input layers
        input_layer = keras.layers.Input(shape=(self.latent_dim,), name='input_layer')

        # apply word embedding to the caption
        caption_input_layer = keras.layers.Input(shape=(self.caption_dim,), name='caption_input_layer')
        embedding_layer  = keras.layers.Embedding(input_dim=vocab_size,
                                                    output_dim=embed_dim,
                                                    name='caption_embedding_layer')
        embed_caption = embedding_layer(caption_input_layer)

        # # source_image_encoding = keras.layers.GlobalAveragePooling2D()(dense4)
        # # using LSTM to encode the caption with the input layer
        # lstm_layer = keras.layers.LSTM(100, return_sequences=True, return_state=True, name="decoder_lstm_layer")
        # decoder_output, decoder_state_h_output, decoder_state_c_output = lstm_layer(embed_caption, initial_state=[input_layer, input_layer])

        # concat the input layer and the caption encoded
        concat_layer = keras.layers.Concatenate(axis=1)([input_layer, embed_caption])

        # apply 1D Global Average Pooling to the output of the dense layer on the caption decoded
        global_average_pooling1d_layer = keras.layers.GlobalAveragePooling1D()(concat_layer)

        # Dense Layer 1
        dense1 = keras.layers.Dense(n_nodes)(global_average_pooling1d_layer)
        leaky_relu1 = keras.layers.LeakyReLU(alpha=0.20)(dense1)
        reshape_layer = keras.layers.Reshape((53, 53, 128))(leaky_relu1)

        # Dense Layer 2
        dense2 =  keras.layers.Dense(1024)(reshape_layer)

        # Conv2DTranspose Layer
        conv2d_transpose = keras.layers.Conv2DTranspose(1024, (4, 4), strides=(2, 2), padding='same')(dense2)

        # Dense Layer 3
        dense3 =  keras.layers.Dense(1024)(conv2d_transpose)
        leaky_relu2 = keras.layers.LeakyReLU(alpha=0.20)(dense3)

        # Dense Layer 4
        dense4 =  keras.layers.Dense(512)(leaky_relu2)

        # Conv2D Layer
        conv2d = keras.layers.Conv2D(1, (7, 7), padding='same', activation='sigmoid')(dense4)

        # Create the model
        model = keras.Model(inputs=[input_layer,caption_input_layer], outputs=conv2d, name='generator')
        return model


    def plot_model(self):
        return keras.utils.plot_model(self.model, show_shapes=True, show_layer_names=True)