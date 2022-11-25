
# more efficient, but less robust and modified to work for the application
class PID_Modified: 

    def __init__(self,kp, ki, kd, sampletime):
        # gains
        self.kp = kp
        self.ki = ki
        self.kd = kd

        # low pass filt
        self.tau = 5
        # print("tau is zero here")

        # output and output limits
        self.out = 0
        self.lim_min = 0
        self.lim_max = 0

        # sample time, delta t
        self.T = sampletime

        # controller state
        self.integrator = 0
        self.differen= 0
        self.prev_verror = 0
        self.prev_vmeas = 0
        self.prev_derror = 0
        self.prev_dmeas = 0
        

    def set_kp(self, val):
        self.kp = val 

    def set_ki(self, val):
        self.ki = val 

    def set_kd(self, val):
        self.kd = val 

    def set_limits(self, min, max):
        self.lim_min = min
        self.lim_max = max

    def update(self, target_dis, measurement_dis, target_vel, measurement_vel):
        # error signal
        derror = target_dis - measurement_dis
        verror = target_vel - measurement_vel

        # proportional term 
        proportional = self.kp * derror

        # integral term
        self.integrator = self.integrator + 0.5* self.ki * self.T * (verror + self.prev_verror)

        # determine integrator limits (dynamic integrator clamping)
        limMaxInt = limMinInt = 0

        if self.lim_max > proportional:
            limMaxInt = self.lim_max - proportional
        else:
            limMaxInt = 0

        if self.lim_min < proportional:
            limMinInt = self.lim_min - proportional
        else:
            limMinInt = 0

        # actually clamp the integrator
        if self.integrator > limMaxInt:
            self.integrator = limMaxInt
        elif self.integrator < limMinInt:
            self.integrator = limMinInt

        # derivate term (band limited differentiator )
        self.differen = (2*self.kd*(measurement_vel - self.prev_vmeas)) \
                        + (2*self.tau - self.T * self.differen) \
                        / (2*self.tau + self.T)
        
        self.out = proportional + self.integrator + self.differen

        if self.out > self.lim_max:
            self.out = self.lim_max
        elif self.out  < self.lim_min:
            self.out = self.lim_min

        self.prev_verror = verror
        self.prev_derror = derror
        self.prev_vmeas = measurement_vel
        self.prev_dmeas = measurement_dis

        return self.out

################# 
### UNUSED
#################
class PID: 

    def __init__(self,kp, ki, kd, sampletime):
        # gains
        self.kp = kp
        self.ki = ki
        self.kd = kd

        # low pass filt
        self.tau = 0
        print("tau is zero here")

        # output and output limits
        self.out = 0
        self.lim_min = 0
        self.lim_max = 0

        # sample time, delta t
        self.T = sampletime

        # controller state
        self.integrator = 0
        self.differen= 0
        self.prevError = 0
        self.prevMeasurement = 0
        

    def set_kp(self, val):
        self.kp = val 

    def set_ki(self, val):
        self.ki = val 

    def set_kd(self, val):
        self.kd = val 

    def update(self, target, measurement):
        # error signal
        e = target - measurement

        # proportional term 
        proportional = self.kp * e

        # integral term
        self.integrator = self.integrator + 0.5* self.ki * self.T * (e + self.prevError)

        # determine integrator limits (dynamic integrator clamping)
        limMaxInt = limMinInt = 0

        if self.lim_max > proportional:
            limMaxInt = self.lim_max - proportional
        else:
            limMaxInt = 0

        if self.lim_min < proportional:
            limMinInt = self.lim_min - proportional
        else:
            limMinInt = 0

        # actually clamp the integrator
        if self.integrator > limMaxInt:
            self.integrator = limMaxInt
        elif self.integrator < limMinInt:
            self.integrator = limMinInt

        # derivate term (band limited differentiator )
        self.differen = (2*self.kd*(measurement - self.prevMeasurement)) \
                        + (2*self.tau - self.T * self.differen) \
                        / (2*self.tau + self.T)
        
        self.out = proportional + self.integrator + self.differen

        if self.out > self.lim_max:
            self.out = self.lim_max
        elif self.out  < self.lim_min:
            self.out = self.lim_min

        self.prevError = e
        self.prevMeasurement = measurement

        return self.out

    def set_limits(self, min, max):
        self.lim_min = min
        self.lim_max = max