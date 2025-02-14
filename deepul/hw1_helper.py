from .utils import *

from deepul.models.vqvae import VQVAE


# Question 1
def q1_sample_data_1():
    count = 1000
    rand = np.random.RandomState(0)
    samples = 0.4 + 0.1 * rand.randn(count)
    data = np.digitize(samples, np.linspace(0.0, 1.0, 20))
    split = int(0.8 * len(data))
    train_data, test_data = data[:split], data[split:]
    return train_data, test_data


def q1_sample_data_2():
    count = 10000
    rand = np.random.RandomState(0)
    a = 0.25 + 0.1 * rand.randn(count)
    b = 0.8 + 0.05 * rand.randn(count)
    c = 0.5 + 0.07 * rand.randn(count)
    d = 0.6 + 0.08 * rand.randn(count)
    msk_rnd = rand.rand(count)
    mask1 = np.logical_and(msk_rnd > 0.0, msk_rnd < 0.25)
    mask2 = np.logical_and(msk_rnd > 0.25, msk_rnd < 0.5)
    mask3 = np.logical_and(msk_rnd > 0.5, msk_rnd < 0.75)
    mask4 = np.logical_and(msk_rnd > 0.75, msk_rnd < 1.0)
    samples = np.clip(a * mask1 + b * mask2 + c * mask3 + d * mask4, 0.0, 1.0)
    data = np.digitize(samples, np.linspace(0.0, 1.0, 100))
    split = int(0.8 * len(data))
    train_data, test_data = data[:split], data[split:]
    return train_data, test_data


def visualize_q1_data(dset_type):
    if dset_type == 1:
        train_data, test_data = q1_sample_data_1()
        d = 20
    elif dset_type == 2:
        train_data, test_data = q1_sample_data_2()
        d = 100
    else:
        raise Exception('Invalid dset_type:', dset_type)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.set_title('Train Data')
    ax1.hist(train_data, bins=np.arange(d) - 0.5, density=True)
    ax1.set_xlabel('x')
    ax2.set_title('Test Data')
    ax2.hist(test_data, bins=np.arange(d) - 0.5, density=True)
    print(f'Dataset {dset_type}')
    plt.show()


def q1_save_results(dset_type, part, fn):
    if dset_type == 1:
        train_data, test_data = q1_sample_data_1()
        d = 20
    elif dset_type == 2:
        train_data, test_data = q1_sample_data_2()
        d = 100
    else:
        raise Exception('Invalid dset_type:', dset_type)

    train_losses, test_losses, distribution = fn(train_data, test_data, d, dset_type)
    assert np.allclose(np.sum(distribution), 1), f'Distribution sums to {np.sum(distribution)} != 1'

    print(f'Final Test Loss: {test_losses[-1]:.4f}')

    save_training_plot(train_losses, test_losses, f'Q1({part}) Dataset {dset_type} Train Plot',
                       f'results/q1_{part}_dset{dset_type}_train_plot.png')
    save_distribution_1d(train_data, distribution,
                         f'Q1({part}) Dataset {dset_type} Learned Distribution',
                         f'results/q1_{part}_dset{dset_type}_learned_dist.png')


""" # Question 2
def q2_a_sample_data(image_file, n, d):
    from PIL import Image
    from urllib.request import urlopen
    import io
    import itertools

    im = Image.open(image_file).resize((d, d)).convert('L')
    im = np.array(im).astype('float32')
    dist = im / im.sum()

    pairs = list(itertools.product(range(d), range(d)))
    idxs = np.random.choice(len(pairs), size=n, replace=True, p=dist.reshape(-1))
    samples = [pairs[i] for i in idxs]

    return dist, np.array(samples)


def visualize_q2a_data(dset_type):
    data_dir = get_data_dir(1)
    if dset_type == 1:
        n, d = 10000, 25
        true_dist, data = q2_a_sample_data(join(data_dir, 'smiley.jpg'), n, d)
    elif dset_type == 2:
        n, d = 100000, 200
        true_dist, data = q2_a_sample_data(join(data_dir, 'geoffrey-hinton.jpg'), n, d)
    else:
        raise Exception('Invalid dset_type:', dset_type)
    split = int(0.8 * len(data))
    train_data, test_data = data[:split], data[split:]

    train_dist, test_dist = np.zeros((d, d)), np.zeros((d, d))
    for i in range(len(train_data)):
        train_dist[train_data[i][0], train_data[i][1]] += 1
    train_dist /= train_dist.sum()

    for i in range(len(test_data)):
        test_dist[test_data[i][0], test_data[i][1]] += 1
    test_dist /= test_dist.sum()

    print(f'Dataset {dset_type}')
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.set_title('Train Data')
    ax1.imshow(train_dist)
    ax1.axis('off')
    ax1.set_xlabel('x1')
    ax1.set_ylabel('x0')

    ax2.set_title('Test Data')
    ax2.imshow(test_dist)
    ax2.axis('off')
    ax2.set_xlabel('x1')
    ax2.set_ylabel('x0')

    plt.show()


def visualize_q2b_data(dset_type):
    data_dir = get_data_dir(1)
    if dset_type == 1:
        train_data, test_data = load_pickled_data(join(data_dir, 'shapes.pkl'))
        name = 'Shape'
    elif dset_type == 2:
        train_data, test_data = load_pickled_data(join(data_dir, 'mnist.pkl'))
        name = 'MNIST'
    else:
        raise Exception('Invalid dset type:', dset_type)

    idxs = np.random.choice(len(train_data), replace=False, size=(100,))
    images = train_data[idxs] * 255
    show_samples(images, title=f'{name} Samples')


def q2_save_results(dset_type, part, fn):
    data_dir = get_data_dir(1)
    if part == 'a':
        if dset_type == 1:
            n, d = 10000, 25
            true_dist, data = q2_a_sample_data(join(data_dir, 'smiley.jpg'), n, d)
        elif dset_type == 2:
            n, d = 100000, 200
            true_dist, data = q2_a_sample_data(join(data_dir, 'geoffrey-hinton.jpg'), n, d)
        else:
            raise Exception('Invalid dset_type:', dset_type)
        split = int(0.8 * len(data))
        train_data, test_data = data[:split], data[split:]
    elif part == 'b':
        if dset_type == 1:
            train_data, test_data = load_pickled_data(join(data_dir, 'shapes.pkl'))
            img_shape = (20, 20)
        elif dset_type == 2:
            train_data, test_data = load_pickled_data(join(data_dir, 'mnist.pkl'))
            img_shape = (28, 28)
        else:
            raise Exception('Invalid dset type:', dset_type)
    else:
        raise Exception('Invalid part', part)

    if part == 'a':
        train_losses, test_losses, distribution = fn(train_data, test_data, d, dset_type)
        assert np.allclose(np.sum(distribution), 1), f'Distribution sums to {np.sum(distribution)} != 1'

        print(f'Final Test Loss: {test_losses[-1]:.4f}')

        save_training_plot(train_losses, test_losses, f'Q2({part}) Dataset {dset_type} Train Plot)',
                           f'results/q2_{part}_dset{dset_type}_train_plot.png')
        save_distribution_2d(true_dist, distribution,
                             f'results/q2_{part}_dset{dset_type}_learned_dist.png')
    elif part == 'b':
        train_losses, test_losses, samples = fn(train_data, test_data, img_shape, dset_type)
        samples = samples.astype('float32') * 255
        print(f'Final Test Loss: {test_losses[-1]:.4f}')
        save_training_plot(train_losses, test_losses, f'Q2({part}) Dataset {dset_type} Train Plot',
                           f'results/q2_{part}_dset{dset_type}_train_plot.png')
        show_samples(samples, f'results/q2_{part}_dset{dset_type}_samples.png')


# Question 3 """
""" def q3a_save_results(dset_type, q3_a):
    data_dir = get_data_dir(1)
    if dset_type == 1:
        train_data, test_data = load_pickled_data(join(data_dir, 'shapes.pkl'))
        img_shape = (20, 20)
    elif dset_type == 2:
        train_data, test_data = load_pickled_data(join(data_dir, 'mnist.pkl'))
        img_shape = (28, 28)
    else:
        raise Exception()

    train_losses, test_losses, samples = q3_a(train_data, test_data, img_shape, dset_type)
    samples = samples.astype('float32') * 255

    print(f'Final Test Loss: {test_losses[-1]:.4f}')
    save_training_plot(train_losses, test_losses, f'Q3(a) Dataset {dset_type} Train Plot',
                       f'results/q3_a_dset{dset_type}_train_plot.png')
    show_samples(samples, f'results/q3_a_dset{dset_type}_samples.png') """

# Question 2
def q2a_save_results(q2_a, train_data, test_data):
    train_losses, test_losses, samples = q2_a(train_data, test_data)

    print(f'Final Test Loss: {test_losses[-1]:.4f}')
    save_training_plot(train_losses, test_losses, f'Q2(a) Train Plot',
                       f'results/q2_a_train_plot.png')
                       
    show_samples_2(samples, f'results/q2_a_samples.png')

def q2b_save_results(q2_b, train_data, test_data):
    train_losses, test_losses, samples = q2_b(train_data, test_data)

    print(f'Final Test Loss: {test_losses[-1]:.4f}')
    save_training_plot(train_losses, test_losses, f'Q2(b) Train Plot',
                       f'results/q2_b_train_plot.png')
                       
    show_samples_2(samples, f'results/q2_b_samples.png')

def q2c_save_results(q2_c, train_data, test_data):
    train_losses, test_losses, samples = q2_c(train_data, test_data)

    print(f'Final Test Loss: {test_losses[-1]:.4f}')
    save_training_plot(train_losses, test_losses, f'Q2(c) Train Plot',
                       f'results/q2_c_train_plot.png')
                       
    show_samples_2(samples, f'results/q2_c_samples.png')

""" def q3bc_save_results(dset_type, part, fn):
    data_dir = get_data_dir(1)
    if dset_type == 1:
        train_data, test_data = load_pickled_data(join(data_dir, 'shapes_colored.pkl'))
        img_shape = (20, 20, 3)
    elif dset_type == 2:
        train_data, test_data = load_pickled_data(join(data_dir, 'mnist_colored.pkl'))
        img_shape = (28, 28, 3)
    else:
        raise Exception()

    train_losses, test_losses, samples = fn(train_data, test_data, img_shape, dset_type)
    samples = samples.astype('float32') / 3 * 255

    print(f'Final Test Loss: {test_losses[-1]:.4f}')
    save_training_plot(train_losses, test_losses, f'Q3({part}) Dataset {dset_type} Train Plot',
                       f'results/q3_{part}_dset{dset_type}_train_plot.png')
    show_samples(samples, f'results/q3_{part}_dset{dset_type}_samples.png') """

"""
def visualize_q3b_data(dset_type):
    data_dir = get_data_dir(1)
    if dset_type == 1:
        train_data, test_data = load_pickled_data(join(data_dir, 'shapes_colored.pkl'))
        name = 'Colored Shape'
    elif dset_type == 2:
        train_data, test_data = load_pickled_data(join(data_dir, 'mnist_colored.pkl'))
        name = 'Colored MNIST'
    else:
        raise Exception('Invalid dset type:', dset_type)

    idxs = np.random.choice(len(train_data), replace=False, size=(100,))
    images = train_data[idxs].astype('float32') / 3 * 255
    show_samples(images, title=f'{name} Samples')


def q3d_save_results(dset_type, q3_d):
    data_dir = get_data_dir(1)
    if dset_type == 1:
        train_data, test_data, train_labels, test_labels = load_pickled_data(join(data_dir, 'shapes.pkl'),
                                                                             include_labels=True)
        img_shape, n_classes = (20, 20), 4
    elif dset_type == 2:
        train_data, test_data, train_labels, test_labels = load_pickled_data(join(data_dir, 'mnist.pkl'),
                                                                             include_labels=True)
        img_shape, n_classes = (28, 28), 10
    else:
        raise Exception('Invalid dset type:', dset_type)

    train_losses, test_losses, samples = q3_d(train_data, train_labels, test_data, test_labels, img_shape, n_classes, dset_type)
    samples = samples.astype('float32') * 255

    print(f'Final Test Loss: {test_losses[-1]:.4f}')
    save_training_plot(train_losses, test_losses, f'Q3(d) Dataset {dset_type} Train Plot',
                       f'results/q3_d_dset{dset_type}_train_plot.png')
    show_samples(samples, f'results/q3_d_dset{dset_type}_samples.png')


# Question 4
def q4a_save_results(q4_a):
    data_dir = get_data_dir(1)
    train_data, test_data = load_pickled_data(join(data_dir, 'mnist_colored.pkl'))
    img_shape = (28, 28, 3)
    train_losses, test_losses, samples = q4_a(train_data, test_data, img_shape)
    samples = samples.astype('float32') / 3 * 255
    print(f'Final Test Loss: {test_losses[-1]:.4f}')
    save_training_plot(train_losses, test_losses, f'Q4(a) Train Plot',
                       f'results/q4_a_train_plot.png')
    show_samples(samples, f'results/q4_a_samples.png')


def q4b_save_results(q4_b):
    data_dir = get_data_dir(1)
    train_data, test_data = load_pickled_data(join(data_dir, 'mnist_colored.pkl'))
    img_shape = (28, 28, 3)
    train_losses, test_losses, gray_samples, color_samples = q4_b(train_data, test_data, img_shape)
    gray_samples, color_samples = gray_samples.astype('float32'), color_samples.astype('float32')
    gray_samples *= 255
    gray_samples = gray_samples.repeat(3, axis=-1)
    color_samples = color_samples / 3 * 255
    samples = np.stack((gray_samples, color_samples), axis=1).reshape((-1,) + img_shape)

    print(f'Final Test Loss: {test_losses[-1]:.4f}')
    save_training_plot(train_losses, test_losses, f'Q4(b) Train Plot',
                       f'results/q4_b_train_plot.png')
    show_samples(samples, f'results/q4_b_samples.png')


def q4c_save_results(q4_c):
    data_dir = get_data_dir(1)
    train_data, test_data = load_pickled_data(join(data_dir, 'mnist.pkl'))
    train_data, test_data = torch.FloatTensor(train_data).permute(0, 3, 1, 2), torch.FloatTensor(test_data).permute(0, 3, 1, 2)
    train_data = F.interpolate(train_data, scale_factor=2, mode='bilinear')
    test_data = F.interpolate(test_data, scale_factor=2, mode='bilinear')
    train_data, test_data = train_data.permute(0, 2, 3, 1).numpy(), test_data.permute(0, 2, 3, 1).numpy()
    train_data, test_data = (train_data > 0.5).astype('uint8'), (test_data > 0.5).astype('uint8')

    train_losses, test_losses, samples = q4_c(train_data, test_data)
    samples = samples.astype('float32') * 255
    print(f'Final Test Loss: {test_losses[-1]:.4f}')
    save_training_plot(train_losses, test_losses, f'Q4(c) Train Plot',
                       f'results/q4_c_train_plot.png')
    show_samples(samples, f'results/q4_c_samples.png')
"""

# Question 3
def q3ab_save_results(dset_type, part, fn):
    if part == "a":
        dataset_suffix = ""
        channel = 1
    elif part == "b":
        dataset_suffix = "_colored"
        channel = 3
    else:
        raise Exception("Invalid part:", part, "Must be 'a' or 'b'")

    data_dir = get_data_dir(1)
    if dset_type == 1:
        train_data, test_data = load_pickled_data(
            join(data_dir, f"shapes{dataset_suffix}.pkl")
        )
        img_shape = (20, 20, channel)
    elif dset_type == 2:
        train_data, test_data = load_pickled_data(
            join(data_dir, f"mnist{dataset_suffix}.pkl")
        )
        img_shape = (28, 28, channel)
    else:
        raise Exception()

    train_losses, test_losses, samples = fn(train_data, test_data, img_shape, dset_type)
    samples = samples.astype("float32") / channel * 255

    print(f"Final Test Loss: {test_losses[-1]:.4f}")
    save_training_plot(
        train_losses,
        test_losses,
        f"Q3({part}) Dataset {dset_type} Train Plot",
        f"results/q3_{part}_dset{dset_type}_train_plot.png",
    )
    show_samples(samples, f"results/q3_{part}_dset{dset_type}_samples.png")


def q3c_save_results(dset_type, fn):
    data_dir = get_data_dir(1)
    if dset_type == 1:
        train_data, test_data = load_pickled_data(
            join(data_dir, f"shapes_colored.pkl")
        )
        img_shape = (20, 20, 3)
    elif dset_type == 2:
        train_data, test_data = load_pickled_data(
            join(data_dir, f"mnist_colored.pkl")
        )
        img_shape = (28, 28, 3)
    else:
        raise Exception()

    (
        time_list_no_cache,
        time_list_with_cache,
        samples_no_cache,
        samples_with_cache,
    ) = fn(train_data, test_data, img_shape, dset_type)
    samples_no_cache = samples_no_cache.astype("float32") / 3 * 255
    samples_with_cache = samples_with_cache.astype("float32") / 3 * 255

    save_timing_plot(
        time_list_no_cache,
        time_list_with_cache,
        "Q3(c) Timing Plot",
        f"results/q3_c_dset{dset_type}_timing_plot.png",
        time1_label="no cache",
        time2_label="with cache",
    )
    show_samples(samples_no_cache, f"results/q3_c_no_cache_dset{dset_type}_samples.png")
    show_samples(
        samples_with_cache, f"results/q3_c_with_cache_dset{dset_type}_samples.png"
    )

    # bonus

    # load vqvae mode
def load_pretrain_vqvae(name: str):
    data_dir = get_data_dir(1)
    loaded_args = torch.load(join(data_dir, f"vqvae_args_{name}_ft" + ".pth"))
    vqvae = VQVAE(**loaded_args)
    vqvae.load_state_dict(torch.load(join(data_dir, f"vqvae_{name}_ft" + ".pth")))
    return vqvae


def bonusa_save_results(dset_type, fn):
    data_dir = get_data_dir(1)
    if dset_type == 1:
        #  @ load colored mnist
        train_data, _ = load_pickled_data(join(data_dir, "mnist_colored.pkl"))
        img_shape = (28, 28, 3)
        vqvae = load_pretrain_vqvae("colored_mnist")
    elif dset_type == 2:
        train_data, _, _, _ = load_colored_mnist_text(
            join(data_dir, "colored_mnist_with_text.pkl")
        )
        img_shape = (28, 28, 3)
        vqvae = load_pretrain_vqvae("colored_mnist_2")
    else:
        raise Exception()

    # get two images
    images = train_data[:2]
    post_decoded_images = fn(images, vqvae)
    stacked_images = np.concatenate([images, post_decoded_images], axis=0)

    vq_images = stacked_images.astype("float32") / 3 * 255
    show_samples(vq_images, f"results/q4_a_dset{dset_type}_samples.png", nrow=2)

def bonusb_save_results(dset_type, fn):
    data_dir = get_data_dir(1)
    if dset_type == 1:
        #  @ load colored mnist
        train_data, test_data = load_pickled_data(join(data_dir, "mnist_colored.pkl"))
        img_shape = (28, 28, 3)
        vqvae = load_pretrain_vqvae("colored_mnist")
    elif dset_type == 2:
        train_data, test_data, _, _ = load_colored_mnist_text(
            join(data_dir, "colored_mnist_with_text.pkl")
        )
        img_shape = (28, 28, 3)
        vqvae = load_pretrain_vqvae("colored_mnist_2")
    else:
        raise Exception()

    train_losses, test_losses, samples = fn(train_data, test_data, img_shape, dset_type, vqvae)

    # decode? TODO
    samples = samples.astype("float32") / 3 * 255

    print(f"Final Test Loss: {test_losses[-1]:.4f}")
    save_training_plot(
        train_losses,
        test_losses,
        f"Qb(a) Dataset {dset_type} Train Plot",
        f"results/q4_b_dset{dset_type}_train_plot.png",
    )
    show_samples(samples, f"results/q4_b_dset{dset_type}_samples.png")
