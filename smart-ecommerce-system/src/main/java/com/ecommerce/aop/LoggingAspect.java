package com.ecommerce.aop;

import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class LoggingAspect {
    
    private static final Logger logger = LoggerFactory.getLogger(LoggingAspect.class);
    
    @Pointcut("execution(* com.ecommerce.service.*.*(..))")
    public void serviceLayer() {}
    
    @Pointcut("execution(* com.ecommerce.controller.*.*(..))")
    public void controllerLayer() {}
    
    @Before("serviceLayer()")
    public void logServiceMethodEntry(JoinPoint joinPoint) {
        String methodName = joinPoint.getSignature().getName();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        Object[] args = joinPoint.getArgs();
        
        logger.info("Entering service method: {}.{}() with arguments: {}", className, methodName, args);
    }
    
    @After("serviceLayer()")
    public void logServiceMethodExit(JoinPoint joinPoint) {
        String methodName = joinPoint.getSignature().getName();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        
        logger.info("Exiting service method: {}.{}()", className, methodName);
    }
    
    @AfterThrowing(pointcut = "serviceLayer()", throwing = "exception")
    public void logServiceMethodException(JoinPoint joinPoint, Exception exception) {
        String methodName = joinPoint.getSignature().getName();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        
        logger.error("Exception in service method: {}.{}() - {}", className, methodName, exception.getMessage());
    }
    
    @Around("controllerLayer()")
    public Object logControllerExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().getName();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        
        long startTime = System.currentTimeMillis();
        logger.info("Starting execution of controller method: {}.{}", className, methodName);
        
        Object result;
        try {
            result = joinPoint.proceed();
        } catch (Exception e) {
            logger.error("Exception in controller method: {}.{}() - {}", className, methodName, e.getMessage());
            throw e;
        }
        
        long endTime = System.currentTimeMillis();
        long executionTime = endTime - startTime;
        
        logger.info("Completed execution of controller method: {}.{}() in {} ms", className, methodName, executionTime);
        
        return result;
    }
}