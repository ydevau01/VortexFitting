import numpy as np
from scipy.signal import correlate2d
from scipy import optimize

import tools

def correlation_coef(Uw,Vw,u,v):
    corr_x = np.mean(Uw*u)/(np.sqrt(np.mean(Uw**2))*np.sqrt(np.mean(u**2)))
    corr_y = np.mean(Vw*v)/(np.sqrt(np.mean(Vw**2))*np.sqrt(np.mean(v**2)))  
    #print('corr x',corr_x)
    #print('corr y',corr_y)
    R = corr_x*corr_y
    return R

def velocity_model(a, x, y,xCenter,yCenter, gamma, coreR):
    r = np.hypot(x-a.dx[xCenter], y-a.dy[yCenter])
    vel = (gamma/(2 * np.pi * r)) * (1 - np.exp(-(r**2)/(coreR)**2))
    vel = np.nan_to_num(vel)
    u_conv = a.u[xCenter,yCenter] 
    v_conv = a.v[xCenter,yCenter]
    velx = (vel + u_conv)*(-x+a.dx[xCenter])
    vely = (vel + v_conv)*(y-a.dy[yCenter])
    return velx, vely

def full_fit(a, xCenter, yCenter, gamma):
    u_conv = a.u[xCenter, yCenter]
    v_conv = a.v[xCenter, yCenter]
    coreR = 0.1
    corrOld = 0.0
    corr = 0.001
    dist = 3
    while (corr > corrOld):
        #print('loop using dist=',dist)
        corrOld = corr
        coreROld = coreR
        X, Y, Uw, Vw = tools.window(a,xCenter,yCenter,dist)
        coreR = super_fit(a, X, Y, xCenter, yCenter, Uw, Vw, u_conv, v_conv, gamma)
        uMod, vMod = velocity_model(a, X, Y,xCenter,yCenter, gamma, coreR)
        corr = correlation_coef(Uw,Vw,uMod,vMod)
        dist += 1
        #print('Old CoreR',coreROld,'Old corr',corrOld,'New CoreR',coreR,'New corr',corr)
        
    return coreROld, corrOld, dist-2
        
  
def super_fit(a, x, y, xCenter, yCenter, Uw, Vw, velx, vely, gamma):
    x = x.ravel()
    y = y.ravel()
    Uw = Uw.ravel()
    Vw = Vw.ravel()
    
    def fun(coreR):
        r = np.hypot(x-a.dx[xCenter], y-a.dy[yCenter])
        expr2 = np.exp(-r**2/coreR**2)
        z = -gamma/(2*np.pi*r) * (1 - expr2)
        z = np.nan_to_num(z)
        zx = (z + velx)*(-x+a.dx[xCenter]) +Uw
        zy = (-z + vely)*(y-a.dy[yCenter]) -Vw
        zt = np.append(zx,zy)
        return zt       
        
    sol = optimize.least_squares(fun, 0.1, method='lm')
    return float(sol.x)
