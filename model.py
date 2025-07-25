import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.Linear1 = nn.Linear(input_size,hidden_size)
        self.Linear2 = nn.Linear(hidden_size,output_size)

    def forward(self,x):
        x = F.relu(self.Linear1(x))
        x = self.Linear2(x)
        return x
    
    def save(self,filename='model.pth'):
        model_folder_path = r'./model'
        if not os.path.exists(model_folder_path):
            os.mkdir(model_folder_path)
        filename = os.path.join(model_folder_path,filename)
        torch.save(self.state_dict(),filename)

class QTrainer:
    def __init__(self,model,lr,gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(),lr=self.lr)
        self.criterion = nn.MSELoss()
    
    def train_step(self,state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()
