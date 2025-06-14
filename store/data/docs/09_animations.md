ConfigurationAnimationsOn this pageAnimationsAnimating the bar​All transitions between ,  and 
values can be animated, by prepending the animation command in front of any
regular --set or --bar command:sketchybar --animate   \ --bar = ... = \ --set  = ... =where the  is any of the animation curves:linear, quadratic, tanh, sin, exp, circThe  is a positive integer quantifying the number of animation
steps (the duration is the frame count on a 60Hz display, such that the
temporal duration of the animation in seconds is given by  / 60).The animation system always animates between all current values and the
values specified in a configuration command (i.e. --bar or --set commands).Perform multiple animations chained together​If you want to chain two or more animations together, you can do so by simply
changing the property multiple times in a single call, e.g.sketchybar --animate sin 30 --bar y\_offset=10 y\_offset=0will animate the bar to the first offset and after that to the second offset.
You can chain together as main animations as you like and you can change the
animation function in between. This is a nice way to create custom animations
with key-frames. You can also make other properties wait with their animation
till another animation is finished, by simply setting the property that should
wait to its current value in the first animation.A new non-animated --set command targeting a currently animated property will
cancel the animation queue and immediately set the value.A new animated --set command targeting a currently animated property will
cancel the animation queue and immediately begin with the new animation,
beginning at the current state.PreviousQuerying InformationNextType NomenclatureAnimating the barPerform multiple animations chained together