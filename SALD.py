#Author: Vignesh Sathyaseelan
#Email: vsathyas@purdue.edu

import numpy as np,copy,os,time
import matplotlib.pyplot as plt

def main():
    #this function returns the energy and force on a particle (Force calculated using central difference formula) 
    potential = lambda x: (0.05)*(np.sin(x[0]) + np.sin(x[1])) + (0.0015)*(x[0]**2 + x[1]**2)
    #potential = lambda x: x[0]**2 + x[1]**2

    st = time.time()

    grad_p = lambda x,func,h=0.01: -1*np.array([(func([x[0]+h,x[1]])-func([x[0]-h,x[1]]))/2*h, (func([x[0],x[1]+h])-func([x[0],x[1]-h]))/2*h])

    print('Running optimization algorithm...')

    times,positions,velocities = sald(potential=potential,gradient=grad_p,initial_position=[2,8],gamma=10,p0=0.5,alpha=0.1\
                                    ,initial_temp=3*(10**25),max_anneal_cycle=20,max_time=10**5,dt=0.1,save_frequency=10)

    print(f'Finished in {np.round(time.time()-st,2)} seconds')
    plot_PES(potential=potential,xmin=-10,xmax=10,positions=positions)

    return

#this is step A
def position_update(x,v,dt):
    x_new = x + v*dt/2.
    return x_new

#this is step B
def velocity_update(v,F,dt):
    v_new = v + F*dt/2.
    return v_new

def random_velocity_update(v,gamma,T,dt):

    kB = 1.380649 * (10**-23)
    R = np.random.normal()
    c1 = np.exp(-gamma*dt)
    c2 = np.sqrt(1-c1**2)*np.sqrt(kB*T)
    v_new = c1*v + R*c2
    return v_new

def sald(potential, gradient, gamma, p0, alpha, initial_position=None, initial_velocity=None, initial_temp=3*(10**25),max_anneal_cycle=100 ,max_time=10**5, dt = 0.01, save_frequency=10):

    anneal_step = 1
    initial_position = initial_position

    print(f'Running SALD-OPT with initial_point = {initial_position} and intitial temp {initial_temp} for {max_anneal_cycle} anneal cycles and each cycle for {max_time}')
    while anneal_step <= max_anneal_cycle:
        
        #set initial temp for each anneal cycle

        T0 = initial_temp
        print(f'Running anneal cycle {anneal_step}...')

        try: os.remove(f'out_{anneal_step}.txt')
        except: pass

        with open(f'out_{anneal_step}.txt','a') as f:
            f.write('time\tX\tY\n')

        t = 0
        step_number = 0
        positions = []
        velocities = []
        save_times=[]

        if anneal_step == 0 and initial_position == None: x = np.random.normal(10,size=2)
        else: x = initial_position

        if initial_velocity: v = initial_velocity
        else: v = np.random.normal(size=2)

        while t<max_time:

            
            # B
            potential_energy, force = potential(x),gradient(x,potential)
            v = velocity_update(v,force,dt)
            
            #A
            x = position_update(x,v,dt)

            #Temperature Anneal
            T = T0*(alpha**step_number)

            #O
            v = random_velocity_update(v,gamma,T,dt)
            
            #A
            x = position_update(x,v,dt)
            
            # B
            potential_energy, force = potential(x),gradient(x,potential)
            v = velocity_update(v,force,dt)


            if step_number%save_frequency == 0:
                positions += [x]
                velocities += [v]
                save_times += [t]

                with open(f'out_{anneal_step}.txt','a') as f:
                    f.write(f'{t:.3f}\t{x[0]:.3f}\t{x[1]:.3f}\n')
            
            t += dt
            step_number += 1
        
        print(f'Anneal step {anneal_step} done. Optimized to = {x}')
        
        initial_position = x
        anneal_step += 1
        
    
    return save_times, np.array(positions), np.array(velocities)

def plot_PES(potential,xmin,xmax,positions,spacing=0.1,outname='out'):
    
    plt.figure(dpi=250)
    plt.xlim(-xmax,xmax)
    plt.ylim(-xmax,xmax)
    grid_x,grid_y = np.meshgrid(np.arange(-xmax,xmax,spacing), np.arange(-xmax,xmax,spacing))
    plt.contourf(grid_x, grid_y, potential([grid_x,grid_y]))
    plt.scatter(positions[:,0],positions[:,1],color='grey')
    plt.scatter(positions[0,0],positions[0,1],color='black')
    plt.scatter(positions[-1,0],positions[-1,1],color='red')
    plt.savefig(f'{outname}.png')

    return

if __name__ == '__main__':
    main()
