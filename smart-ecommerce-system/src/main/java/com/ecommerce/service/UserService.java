package com.ecommerce.service;

import com.ecommerce.dto.UserDTO;
import com.ecommerce.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Optional;

public interface UserService {
    
    Page<UserDTO> getAllUsers(Pageable pageable);
    
    Optional<UserDTO> getUserById(Long id);
    
    Optional<UserDTO> getUserByUsername(String username);
    
    Optional<UserDTO> getUserByEmail(String email);
    
    UserDTO createUser(UserDTO userDTO);
    
    UserDTO updateUser(Long id, UserDTO userDTO);
    
    void deleteUser(Long id);
    
    List<UserDTO> getUsersByRole(User.Role role);
    
    List<UserDTO> getEnabledUsers(boolean enabled);
    
    boolean existsByUsername(String username);
    
    boolean existsByEmail(String email);
}