import torch

def get_D_loss_batch(D, G, edge_images, original_images, fake_images, bce, device):
    D.eval()
    G.eval()

    with torch.cuda.amp.autocast():
        fake_logits = D(edge_images, fake_images.detach())
        real_logits = D(edge_images, original_images)

        fake_loss = bce(fake_logits, torch.zeros(fake_logits.shape).to(device))
        real_loss = bce(real_logits, torch.ones(real_logits.shape).to(device))
        discriminator_loss = fake_loss + real_loss
        
    D.train()
    G.train()
    return discriminator_loss

def get_G_loss_batch(D, G, edge_images, original_images, fake_images, bce, l1, device):
    D.eval()
    G.eval()

    with torch.cuda.amp.autocast():
        fake_logits = D(edge_images, fake_images)
        fake_loss = bce(fake_logits, torch.ones(fake_logits.shape).to(device))
        l1_loss = 100*l1(fake_images, original_images)
        generator_loss = fake_loss + l1_loss

    D.train()
    G.train()
    return generator_loss

def get_losses_dataset(D, G, data_loader, bce, l1, device, num_batches=None):
    num_images = 0
    discriminator_loss = 0
    generator_loss = 0

    D.eval()
    G.eval()
    for edge_images, original_images in data_loader:
        num_images += original_images.shape[0]

        edge_images = edge_images.to(device)
        original_images = original_images.to(device)
        fake_images = G(edge_images)

        discriminator_loss += get_D_loss_batch(D, G, edge_images, original_images, fake_images, bce, device)
        generator_loss += get_G_loss_batch(D, G, edge_images, original_images, fake_images, bce, l1, device)

        if num_batches is not None:
            if num_batches == 0:
                break
            else:
                num_batches -= 1

    D.train()
    G.train()
    return discriminator_loss/num_images, generator_loss/num_images
