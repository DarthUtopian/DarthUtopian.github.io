---
published: True
layout: post
title: Variational Inference for Policy Optimization 
date: 2026-01-23 11:12:00-0400
description: an example of a blog post with some math
tags: RL
categories: sample-posts
related_posts: true
related_publications: false
citation: true
authors:
  - name: Haotian Lin
    url: "https://DarthUtopian.github.io"
    affiliations:
      name: Carnegie Mellon University
---

$$
\newcommand{\coloneqq}{\mathrel{\vcenter{:}}=}
$$

This blog is mainly inspired by [MPO](https://arxiv.org/abs/1806.06920), an off-policy RL framework based on coordinate ascent on a relative entropy objective. We will briefly discuss how this framework relates to various RL paradigms, including trust-region policy optimization (TRPO) families and Max-Ent RL algorithms (More discussion can be found in this amazing [tutorial paper](https://arxiv.org/pdf/1805.00909)).


## RL as Structured Variational Inference.

In **structured variational inference**, the goal is to approximate a distribution with another similar distribution (density estimation). In general, the reinforcement learning objective can be viewed as optimizing an expectation over a **parameterized distribution** given an MDP  $\mathcal{M}(S, A, \gamma, p, R)$:

$$
\arg\max_\theta \mathbb{E}_{\tau \sim \pi_\theta}\Big[\sum_{t=1} \gamma^{t-1} r_t \Big] \tag{1}
$$

Denote  $\tau$ as a trajectory and  $\pi$ as a existing distribution of trajectories (current policy), consider translating this target as maximizing the likelihood of $\tau \sim \pi$ being optimal. We first introduce a binary-value variable $O$ that describes the optimality of a given trajectory $\tau$(1 indicates $\tau$ being optimal and 0 on the opposite). Define the prior probability of a trajectory being optimal as $p(O=1|\tau)\propto \exp^{\frac{1}{\alpha}\Sigma_\tau r(s_t, a_t)}$ 

NOTE: For an infinite horizon MDP, consider discounted return:   $\Sigma_t \gamma^{t-1} r(s_t, a_t)$). We omit the normalization constant of the prior distribution, as it is independent of the optimization variables and therefore does not affect the resulting objective. Moreover, we set the temperature coefficient $\alpha = 1$ without loss of generality for now.

$$
\begin{aligned} \log p_\pi(O) & \coloneqq \log \int_\tau p(O | \tau) \pi(\tau) d\tau \\      &\geq \mathbb{E}_{q}\left[ \log p(O|\tau) - \log\frac{q(\tau)}{\pi(\tau)} \right] \\    &= \mathbb{E}_q[\log p(O|\tau)] - \mathbf{D}_{KL}(q(\tau) \Vert \pi(\tau)) \\ &= \sum_t  \mathbb{E}_{(s_t, a_t)\sim q}[r(s_t, a_t)] - \mathbb{E}_{s_t \sim q}\mathbf{KL}(q(\cdot |s_t)\Vert \pi(\cdot|s_t)) \end{aligned} \tag{2}
$$

Here, we introduce an auxiliary distribution $q$, which can be translated into another policy.

This formulation resembles the ELBO of a variational auto-encoder (VAE).

Next, consider optimizing this lower bound through **coordinate ascent**. 

The objective of $q$ is the KL-regularized return (not caring about the partition):

$$
J_q (s_0) = \mathbb{E}_{q(\tau | s_0)} \left[ \sum_t \gamma^t r(s_t, a_t) - \mathbf{D}_{KL}(q(a_T | s_t) \Vert \pi(a_t | s_t)  \right] \tag{3}
$$

$$
J_q (s_0) = \mathbb{E}_{q(\tau | s_0)} \left[ \sum_t \gamma^t r(s_t, a_t) + \mathbf{H}[q(a_t | s_t)]  \right] \tag{4}
$$

Another comparision is:

$$
J_q (s_0) = \mathbb{E}_{q(\tau | s_0)} \left[ \sum_t \gamma^t r(s_t, a_t) - \log q(a_T | s_t) + \log \pi(a_t | s_t)  \right] \tag{5}
$$

$$
J_q (s_0) = \mathbb{E}_{q(\tau | s_0)} \left[ \sum_t \gamma^t r(s_t, a_t) - \log q(a_T | s_t)  \right] \tag{6}
$$

Thus, define the action value function and the value KL-regularized Bellman function as:

$$
Q^q(s_t, a_t) \coloneqq r(s_t, a_t) + \mathbb{E}_{q} \left[ \sum_{k=t+1} \gamma^k r(s_k, a_k) - \mathbf{D}_{KL}(q(a_k | s_k) \Vert \pi(a_k | s_k)  \right] 
$$

$$
\mathcal{T}^{\pi, q} Q^q(s_t, a_t) \coloneqq r(s_{t}, a_{t}) + \gamma \mathbb{E}_{p_q(s_{t+1}, a_{t+1}| s_t, a_t)} \left[Q^q (s_{t+1}, a_{t+1}) - \frac{\log q(a_{t+1}|s_{t+1})}{\log \pi(a_{t+1}|s_{t+1})}\right] 
$$

Then, express the objective within the context of policy iteration:

$$
q_{k}(a|s) = \arg \max_q  \mathbb{E}_{q} [Q^{q_{k-1}}(s, a)] - \mathbf{D}_{KL}(q(a|s) \Vert \pi_k(a|s) ) \tag{7}
$$

This can be considered as the **E-step** of the EM algorithm; Thus, the corresponding **M-step** is:

$$
\pi_{k+1}(a|s) = \arg \min_\pi \mathbf{D}_{KL}(q(a|s) \Vert \pi(a|s)) \tag{8}
$$

One may formulate an iterative algorithm either considering:

- Parameterized E-step + Unparameterized M-step: Optimize parameterized $q_\theta$ via (7)
- Parameterized M-step + Unparameterized E-step: Solve for the closed form in (7) and optimize parameterized $\pi_\theta$ via (8).


## Connection to Max-Ent RL

If considering the cross entropy $\mathbb{E}_q[\log \pi]$ as part of the reward (we can consider solving a different MDP that incentivizes a similar behavior to $\pi$), with the following definition of the action-value function:

$$
Q \coloneqq  r(s_t, a_t) + \log \pi + \mathbb{E}_{\{s_{t+1}, ...\}\sim q} \left[ \sum_{k=t+1} \gamma^k r(s_k, a_k) - \mathbf{D}_{KL}(q(a_k | s_k) \Vert \pi(a_k | s_k)  \right]
$$

$$
\mathcal{T}^{\pi, q} Q(s_t, a_t) \coloneqq r(s_{t}, a_{t}) + \log \pi + \gamma \mathbb{E}_{p_q(s_{t+1}, a_{t+1}| s_t, a_t)} \left[Q (s_{t+1}, a_{t+1}) - \log q(a_{t+1}|s_{t+1})\right] 
$$

Thus, the iterative objective of $q$ is:

$$
q_{k}(a|s) = \arg \max_q  \mathbb{E}_{q} [Q^{q_{k-1}}(s, a) - \log q_{k-1}] \tag{9}
$$

Trivially, if we define $\pi$ as a uniform distribution, the equivalence seems to be obvious. However, it is not straightforward to translate (2). We reformulate the **variational inference** problem as: 

$$
\begin{aligned} \log p(O) & \coloneqq \log \int_\tau p(O, \tau) d\tau \\      &\geq \mathbb{E}_{q}\left[ \log p(O,\tau) - \log q(\tau) \right] \\    &= \mathbb{E}_{q} \left[ \sum_t r(s_t, a_t) - \log q(a_t | s_t) + C \right] \\ &= \sum_t  \mathbb{E}_{(s_t, a_t)\sim q}[r(s_t, a_t)] + \mathbb{E}_{s_t \sim q}\mathcal{H}(q(\cdot |s_t)) + C  \end{aligned} \tag{10}
$$

The final equality is given by the fact that

$$
\begin{aligned} p(O, \tau) &= p(s_0) \prod_{t} p(s_{t+1} | s_t, a_t) p(O_t | s_t, a_t) \\ &\propto p(s_0)\prod_{t} e^{r(s_t, a_t)} p(s_{t+1} | s_t, a_t) \\ &= \left(p(s_0)\prod_t p(s_{t+1} | s_t, a_t)\right) e^{\sum_t r(s_t, a_t)} \end{aligned} \tag{11}
$$

and

$$
q(\tau) = p(s_0) \prod_t p(s_{t+1}|s_t, a_t) q(a_t | s_t) \tag{12}
$$

Hence, we arrive at the **maximum entropy objective**. The distinction between (2) and (10) reveals different perspectives when optimizing the policy. The former considers optimizing it given the current behavior, while the latter emphasizes finding a global optimal.


## References
[1] Schulman, John, et al. "Trust region policy optimization." International conference on machine learning. PMLR, 2015.

[2] Abdolmaleki, Abbas, et al. "Maximum a posteriori policy optimisation." arXiv preprint arXiv:1806.06920 (2018).

[3] Song, H. Francis, et al. "V-mpo: On-policy maximum a posteriori policy optimization for discrete and continuous control." arXiv preprint arXiv:1909.12238 (2019).

[4] Haarnoja, Tuomas, et al. "Soft actor-critic: Off-policy maximum entropy deep reinforcement learning with a stochastic actor." International conference on machine learning. Pmlr, 2018.

[5] Levine, Sergey. "Reinforcement learning and control as probabilistic inference: Tutorial and review." arXiv preprint arXiv:1805.00909 (2018).