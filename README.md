# Testing Capsule Network on various datasets

## Included datasets
* mnist
* fashion-mnist
* affnist

## Network Model
* baseline_network (Convolutional Neural Network)
* capsule_dynamic (Capsule Network with Dynamic Routing)
* *capsule_em* (ToDo)

## Training
```
$ python main.py --model=capsule_dynamic --data=mnist
```

## Testing
```
$ python main.py --is_train=False --model=capsule_dynamic --data=mnist
```

### Test 1
| Train | Test |
| ------------- | ------------- |
| mnist  | mnist (random rotation -60 to +60) |

```
$ python main.py --model=capsule_dynamic --data=mnist
```
```
$ python main.py --is_train=False --model=capsule_dynamic --data=mnist --rotate=True
```

### Test 2 
| Train | Test |
| ------------- | ------------- |
| fashion-mnist  | fashion-mnist |

```
$ python main.py --model=capsule_dynamic --data=fashion-mnist 
```

```
$ python main.py --is_train=False --model=capsule_dynamic --data=fashion-mnist 
```

### Test 3
| Train | Test |
| ------------- | ------------- |
| mnist (randomly placed mnist on 40x40 background) | affnist |
```
$ python main.py --model=capsule_dynamic --data=mnist --random_pos=True
```

```
$ python main.py --is_train=False --model=capsule_dynamic --data=affnist
```
