import numpy as np  
import freud
import gsd, gsd.hoomd 
import hoomd 
import time

from dpd_utils import initialize_snapshot_rand_walk,check_bond_length_equilibration,check_inter_particle_distance,add_hoomd_writers,check_pair_energy


def create_polymer_system_dpd(num_pol,num_mon,density,gsd_path,log_path,k=20000,bond_l=1.0,r_cut=1.15,kT=1.0,A=1000,gamma=800,dt=0.001,particle_spacing=1.1,sim_seed=123,np_seed=1234,write=True,energy=True):
    
    '''
    Initialize a polymer system in a cubic box using a random walk and a HOOMD simulation with DPD forces.

    ----------
    Parameters
    ----------
    num_pol : int, required
        number of polymers in system
    num_mon : int, required
        length of polymers in system
    density : float, required
        number density to initalize the system
    k : int, default 20000
        spring constant for harmonic bonds
    bond_l : float, default 1.0
        harmonic bond rest length
    r_cut : float, default 1.15
        cutoff pair distance for neighbor list
    kT : float, default 1.0
        temperature of thermostat
    A : float, default 1000
        DPD force parameter
    gamma : float, default 800
        DPD drag parameter (mass/time)
    dt : float, default 0.001
        timestep for HOOMD simulation
    particle_spacing : float, default 1.1
        condition for ending the soft push simulation
    sim_seed : int, default 123
        random seed for the HOOMD simulation state
    np_seed : int, default 1234
        seed for random number generator in random walk

    -------
    Returns
    -------
    
    positions : list
        returns list of particle positions
        
    '''
    print(num_pol*num_mon)
    print(f"\nRunning with A={A}, gamma={gamma}, k={k}, "
          f"num_pol={num_pol}, num_mon={num_mon}")
    start_time = time.perf_counter()
    frame = initialize_snapshot_rand_walk(num_mon=num_mon,num_pol=num_pol,bond_length=bond_l,density=density,seed=np_seed)
    build_stop = time.perf_counter()
    build_time = build_stop-start_time
    print("Total build time: ", build_time)
    harmonic = hoomd.md.bond.Harmonic()
    print("0")
    harmonic.params["b"] = dict(r0=bond_l, k=k)
    print("1")
    integrator = hoomd.md.Integrator(dt=dt)
    print("2")
    integrator.forces.append(harmonic)
    print("3")
    simulation = hoomd.Simulation(device=hoomd.device.auto_select(), seed=np.random.randint(sim_seed))
    print("4")
    simulation.operations.integrator = integrator 
    print("5")
    try:
        simulation.create_state_from_snapshot(frame)
    except:
        print("womp")
    print("6")
    const_vol = hoomd.md.methods.ConstantVolume(filter=hoomd.filter.All())
    print("7")
    integrator.methods.append(const_vol)
    print("8")
    nlist = hoomd.md.nlist.Cell(buffer=0.4)
    print("9")
    simulation.operations.nlist = nlist
    print("10")
    DPD = hoomd.md.pair.DPD(nlist, default_r_cut=r_cut, kT=kT)
    print("11")
    DPD.params[('A', 'A')] = dict(A=A, gamma=gamma)
    print("12")
    integrator.forces.append(DPD)
    print("13")
    
    if write:
        print("14")
        add_hoomd_writers(simulation, gsd_path=gsd_path, log_path=log_path)
        print("15")
    simulation.run(0) 
    print("16")
    for writer in simulation.operations.writers:
        print("17")
        if hasattr(writer, "flush"):
            print("18")
            writer.flush()
            print("19")
    simulation.run(500)
    print("20")
    for writer in simulation.operations.writers:
        print("21")
        if hasattr(writer, "flush"):
            print("22")
            writer.flush()
            print("23")
    snap=simulation.state.get_snapshot()
    print("24")

    if energy:
        shrink_cut = 5
        print("25")
        while not check_pair_energy(shrink_cut): 
            print("26")
            check_time = time.perf_counter()
            print("27")
            if (check_time-start_time) > 60:
                print("28")
                return num_pol*num_mon, 0
            print("29")
            simulation.run(1000)
            print("30")
            for writer in simulation.operations.writers:
                print("31")
                if hasattr(writer, "flush"):
                    print("32")
                    writer.flush()
                    print("33")
            snap=simulation.state.get_snapshot()
            print("34")
            shrink_cut += 50
            print("35")
    else:
        print("36")
        while not check_inter_particle_distance(snap,minimum_distance=0.95):
            print("37")
            check_time = time.perf_counter()
            print("38")
            if (check_time-start_time) > 7200:
                print("39")
                return 0
            print("40")
            simulation.run(100)
            print("41")
            for writer in simulation.operations.writers:
                print("42")
                if hasattr(writer, "flush"):
                    print("43")
                    writer.flush()
                    print("44")
            snap=simulation.state.get_snapshot()
            print("45")
        
    end_time = time.perf_counter()
    print("46")
    total_time = end_time - start_time
    print("47")
    print("Total build and simulation time:", end_time - start_time)
    print("48")
    return build_time, total_time, simulation.timestep, 
