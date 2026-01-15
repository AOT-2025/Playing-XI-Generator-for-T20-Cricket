# 🔹 File: mlp_trainer.py

import torch
import torch.nn as nn
import torch.optim as optim

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train_mlp(X_np, y_np, iyengar_w=None, epochs=100, lr=0.001):
    class MLP(nn.Module):
        def __init__(self, input_dim, iyengar_w=None):
            super().__init__()
            self.fc1 = nn.Linear(input_dim, 64)
            if iyengar_w is not None:
                with torch.no_grad():
                    weight_matrix = torch.tensor(iyengar_w, dtype=torch.float32).repeat(64, 1)
                    self.fc1.weight.copy_(weight_matrix)
                    self.fc1.bias.fill_(0)
            else:
                nn.init.xavier_uniform_(self.fc1.weight)
                nn.init.zeros_(self.fc1.bias)

            self.relu = nn.ReLU()
            self.fc2 = nn.Linear(64, 1)
            nn.init.zeros_(self.fc2.weight)
            nn.init.zeros_(self.fc2.bias)

        def forward(self, x):
            x = self.relu(self.fc1(x))
            return self.fc2(x)

    X_t = torch.tensor(X_np, dtype=torch.float32).to(device)
    y_t = torch.tensor(y_np, dtype=torch.float32).view(-1, 1).to(device)

    model = MLP(X_np.shape[1], iyengar_w).to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(X_t)
        loss = criterion(output, y_t)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        preds = model(X_t).cpu().numpy().flatten()

    return preds
