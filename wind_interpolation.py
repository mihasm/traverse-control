import numpy
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import scipy.linalg
import scipy.interpolate
import matplotlib.cm as cm
from mpldatacursor import datacursor
from sympy.solvers import solve
from sympy import Symbol, Eq

def create_approximation_plane(x,y,z,_print=False,order=1):
    data = np.c_[x,y,z]
    mn = np.min(data, axis=0)
    mx = np.max(data, axis=0)
    X,Y = np.meshgrid(np.linspace(mn[0], mx[0], 5), np.linspace(mn[1], mx[1], 5))

    XX = X.flatten()
    YY = Y.flatten()

    #order = 1  # 1: linear, 2: quadratic
    if order == 1:
        # best-fit linear plane
        A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
        C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])    # coefficients
        if _print:
            print(C[0],"x +",C[1],"y +",C[2])
        # evaluate it on grid
        Z = C[0]*X + C[1]*Y + C[2]

        def plane_function(X,Y,_print=False):
            return  C[0]*X + C[1]*Y + C[2]
        
        # or expressed using matrix/vector product
        Z = np.dot(np.c_[XX, YY, np.ones(XX.shape)], C).reshape(X.shape)

    elif order == 2:
        # best-fit quadratic curve
        A = np.c_[np.ones(data.shape[0]), data[:,:2], np.prod(data[:,:2], axis=1), data[:,:2]**2]
        C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])
        if _print:
            print(C[4],"x^2 +",C[5],"y^2 + ",C[3],"xy +",C[1],"x +",C[2],"y +",C[0])
        def plane_function(X,Y,_print=False):
            return C[4]*X**2. + C[5]*Y**2. + C[3]*X*Y + C[1]*X + C[2]*Y + C[0]
        
        # evaluate it on a grid
        Z = np.dot(np.c_[np.ones(XX.shape), XX, YY, XX*YY, XX**2, YY**2], C).reshape(X.shape)
    return X,Y,Z, plane_function, C


def draw_colormap(x,y,z,absolute_scale=False,absolute_min=0,absolute_max=30):
    # Ne vem ali je to potrebno. Menda je.
    x = numpy.array(x)
    y = numpy.array(y)
    z = numpy.array(z)
    # x/y tocke za risati ozadje
    xi, yi = numpy.linspace(x.min(), x.max(), 100), numpy.linspace(y.min(), y.max(), 100)
    xi, yi = numpy.meshgrid(xi, yi)
    # Linearna interpolacija ozadja, glede na x,y,z
    rbf = scipy.interpolate.Rbf(x, y, z, function='cubic')
    zi = rbf(xi, yi)

    plt.imshow(zi, vmin=z.min(), vmax=z.max(), origin='lower',
                extent=[x.min(), x.max(), y.min(), y.max()], cmap=cm.jet)
    if absolute_scale:
        plt.clim(absolute_min,absolute_max) #absolutne vrednosti colormapa

    plt.xlim(-1000,0)
    plt.ylim(-1000,0)

    plt.xlabel('Min:%.2f Max:%.2f Avg:%.2f' % (z.min(),z.max(),numpy.mean(z)))
    
    plt.scatter(x, y, c=z, cmap=cm.jet)
    #if absolute_scale:
    #   plt.clim(absolute_min,absolute_max) #absolutne vrednosti colormapa
    
    plt.colorbar()
    #folder_name, file_name = os.path.split(traverse_locations)
    #plt.title(predpona+file_name)
    #if prikazi:
    plt.show()

def get_approximation_planes(order=1):
    f = open(os.path.join('results','all_data.csv'),'r')

    data = {}

    for line in f.readlines()[1:]:
        x,y,z,date,vel,vel_u,temp,temp_u,perc,perc_str = line.strip()[:-1].split(',')
        x = float(x)
        y = float(y)
        z = float(z)
        if not (x,y,z) in data:
            data[(x,y,z)] = []
        data[(x,y,z)].append([vel,temp,perc])

    all_points =  {}

    for loc,dat in data.items():
        all_vel = []
        all_temp = []
        all_perc = []
        for d in dat:
            all_vel.append(float(d[0]))
            all_temp.append(float(d[1]))
            all_perc.append(float(d[2]))
        all_points[loc] = {"all_vel":all_vel,"all_temp":all_temp,"all_perc":all_perc}

    approximation_functions = {}

    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    #ax.set_xlabel('Procent vetrovnika [%]')
    #ax.set_ylabel('Temperatura [C]')
    #ax.set_zlabel('Hitrost vetra [m/s]')

    for k in all_points:
        
        x = all_points[k]['all_perc']
        y = all_points[k]['all_temp']
        z = all_points[k]['all_vel']

        #print(k,':')
        X,Y,Z,func,C = create_approximation_plane(x,y,z,order=order,_print=False)
        
        approximation_functions[k] = func
        #surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, alpha=0.2,label=str(k))

        """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x,y,z)
        ax.plot_surface(X, Y, Z, rstride=1, cstride=1, alpha=0.2)
        plt.title("x:"+str(-k[1])+" y:"+str(-k[2]))
        plt.xlabel('Procent vetrovnika [%]')
        plt.ylabel('Temperatura [C]')
        plt.show()
        """
    #datacursor()
    #plt.show()
    return approximation_functions


def _generate_wind(percentage_wind_tunnel,temperature,approximation_functions):

    all_x = []
    all_y = []
    all_z = []

    for k,ff in approximation_functions.items():
        x,y,z = -k[1], -k[2], ff(percentage_wind_tunnel,temperature)
        all_x.append(x)
        all_y.append(y)
        all_z.append(z)

    return all_x,all_y,all_z

def get_average_plane():
    approximation_functions = get_approximation_planes()
    all_i = []
    all_j = []
    all_k = []
    for i in np.linspace(0,100,10):
        for j in np.linspace(0,40,10):
            X,Y,Z = _generate_wind(percentage_wind_tunnel=i,temperature=j,approximation_functions=approximation_functions)
            #draw_colormap(X,Y,Z)
            k = np.mean(Z)
            all_i.append(i)
            all_j.append(j)
            all_k.append(k)
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(all_i,all_j,all_k)
    plt.xlabel('Procent vetrovnika [%]')
    plt.ylabel('Temperatura [C]')
    plt.show()
    """

    X1,Y1,Z1,func,C = create_approximation_plane(all_i,all_j,all_k,order=1,_print=False)
    return X1,Y1,Z1,func,C


def generate_wind(percentage_wind_tunnel,temperature):
    approximation_functions = get_approximation_planes(1)
    X,Y,Z = _generate_wind(percentage_wind_tunnel,temperature,approximation_functions=approximation_functions)
    return X,Y,Z,np.mean(Z)

def get_percentage(temperature,desired_speed):
    #draw_colormap(X1,Y1,Z1)
    X2,Y2,Z2,avg_func,C = get_average_plane()
    a,b,c = C
    p = Symbol('p')
    T = Symbol('T')
    v = Symbol('v')
    eq = Eq(a*p+b*T+c,v)
    s = solve(eq,p)
    needed_percentage = s[0].subs({T:temperature, v:desired_speed})
    print("To reach %s m/s @ %s degC, the wind tunnel percentage has to be %s %%." % (desired_speed,temperature,needed_percentage))

X1,Y1,Z1,avg = generate_wind(percentage_wind_tunnel=40,temperature=25)
draw_colormap(X1,Y1,Z1)
#get_percentage(temperature=25,desired_speed=10)
#X,Y,Z,func,C = get_average_plane()
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#ax.scatter(x,y,z)
#ax.plot_surface(X, Y, Z, rstride=1, cstride=1, alpha=0.2)
#plt.show()

