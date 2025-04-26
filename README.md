## Some methods to reduce latency from github
# Watsonx.ai - Latency Reduction with Asynchronous API Calls

## Background

In the pursuit of performance optimization and user experience enhancement, our team initiated an internal project focused on decreasing the response latency of four essential API calls, each performing unique functions within our system. The common challenge across these API calls was significant latency, which impacted system efficiency and user satisfaction adversely.

To address this challenge effectively, our strategy involved the implementation of asynchronous multi-threading techniques. This method enabled the simultaneous execution of all four API calls. Such an approach resulted in a significant reduction of overall latency to slightly more than the duration of the longest single API call. The outcomes of this project not only surpassed our initial expectations but also established a new standard for operational efficiency in our subsequent projects.

#### Note that this works only for Independent API calls which can be multi-threaded. There shouldn't be any dependency on these calls. 

## Approaches

### Approach 1: Concurrent.futures

- *Description:* Utilizes the Concurrent.futures module to manage a pool of threads, facilitating non-blocking API calls.
- *Pros:* Offers the fastest response times with a straightforward configuration process.
- *Cons:* Basic, but highly effective for the tasks at hand.

### Approach 2: AsyncIO

- *Description:* Implements the AsyncIO library for asynchronous programming, handling tasks with a more complex setup.
- *Pros:* Delivers comparable response timings to Concurrent.futures, showcasing its efficiency in asynchronous operations.
- *Cons:* Configuration is mildly more complicated, requiring a deeper understanding of asynchronous programming.

### Approach 3: Inbuilt async_mode

- *Description:* Leverages the inbuilt async_mode feature available in certain frameworks or libraries to perform asynchronous calls.
- *Pros:* Integrates easily with existing systems, offering a good balance between performance and ease of use.
- *Cons:* Requires additional formatting for the output, and the percentage improvement in latency is slightly less than the other approaches.

### Approach 4: Single Prompting

- *Description:* A unique method that focuses on minimizing the number of API calls for larger input sizes by using a single, comprehensive prompt.
- *Pros:* Reduces the number of required API calls, potentially lowering costs and system load.
- *Cons:* Faces limitations with token limits for bigger input sizes, and the model's output may not be consistent, with occasional inaccuracies.

## Business Impact

The implementation of these asynchronous API calls has had a significant positive impact on our business operations:

- *User Experience:* By reducing the latency by nearly 50%, we've substantially improved the responsiveness of our system, leading to higher user satisfaction.
- *Scalability:* The flexibility offered by employing multiple models for handling API calls enhances our system's ability to scale, accommodating an increasing number of requests without a proportional increase in latency.

## Conclusion

Watsonx.ai's initiative to reduce API response latency through asynchronous calls has demonstrated the power of innovative thinking in solving performance challenges. By embracing different approaches and continuously seeking the most effective solutions, we not only improve our systems but also ensure that our users receive the fast, reliable service they deserve.
